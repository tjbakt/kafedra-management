from collections import defaultdict
from decimal import Decimal

from django.db.models import (
    Case,
    DecimalField,
    F,
    Q,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce

from apps.staff.models import StaffEmploymentAcademicYear
from apps.teaching.models import PlannedWorkload
from apps.workload.models import WorkloadDistribution


class AcademicYearWorkloadValidationService:
    """
    Проверяет согласованность плановой и распределённой
    учебной нагрузки за выбранный учебный год.

    Сервис ничего не изменяет в базе данных.
    """

    class Severity:
        ERROR = "error"
        WARNING = "warning"

        CHOICES = (
            ERROR,
            WARNING,
        )

    class IssueType:
        PLANNED_WITHOUT_DISTRIBUTIONS = (
            "planned_without_distributions"
        )
        PLANNED_PARTIALLY_DISTRIBUTED = (
            "planned_partially_distributed"
        )
        PLANNED_HOURS_EXCEEDED = (
            "planned_hours_exceeded"
        )
        PLANNED_STATUS_MISMATCH = (
            "planned_status_mismatch"
        )

        DISTRIBUTION_DRAFT = "distribution_draft"
        APPROVAL_DATA_MISSING = "approval_data_missing"
        APPROVAL_DATA_UNEXPECTED = (
            "approval_data_unexpected"
        )

        EMPLOYMENT_ARCHIVED = "employment_archived"
        EMPLOYMENT_INACTIVE = "employment_inactive"
        NON_TEACHING_POSITION = "non_teaching_position"
        EMPLOYMENT_DEPARTMENT_MISMATCH = (
            "employment_department_mismatch"
        )
        YEAR_STAFF_RECORD_MISSING = (
            "year_staff_record_missing"
        )
        WORKLOAD_NORM_MISSING = "workload_norm_missing"
        TEACHER_OVERLOADED = "teacher_overloaded"

        CHOICES = (
            PLANNED_WITHOUT_DISTRIBUTIONS,
            PLANNED_PARTIALLY_DISTRIBUTED,
            PLANNED_HOURS_EXCEEDED,
            PLANNED_STATUS_MISMATCH,
            DISTRIBUTION_DRAFT,
            APPROVAL_DATA_MISSING,
            APPROVAL_DATA_UNEXPECTED,
            EMPLOYMENT_ARCHIVED,
            EMPLOYMENT_INACTIVE,
            NON_TEACHING_POSITION,
            EMPLOYMENT_DEPARTMENT_MISMATCH,
            YEAR_STAFF_RECORD_MISSING,
            WORKLOAD_NORM_MISSING,
            TEACHER_OVERLOADED,
        )

    ACTIVE_DISTRIBUTION_STATUSES = (
        WorkloadDistribution.Status.DRAFT,
        WorkloadDistribution.Status.APPROVED,
    )

    EXPECTED_PLANNED_STATUS_BY_STATE = {
        "empty": PlannedWorkload.Status.APPROVED,
        "partial": PlannedWorkload.Status.PARTIALLY_DISTRIBUTED,
        "full": PlannedWorkload.Status.DISTRIBUTED,
        "exceeded": PlannedWorkload.Status.DISTRIBUTED,
    }

    @classmethod
    def validate(
        cls,
        *,
        academic_year,
        department_ids=None,
        severity=None,
        issue_type=None,
    ) -> dict:
        """
        Возвращает полный отчёт проверки.

        department_ids:
            None — проверяются все кафедры;
            iterable — только перечисленные кафедры.
        """

        cls._validate_filters(
            severity=severity,
            issue_type=issue_type,
        )

        normalized_department_ids = (
            None
            if department_ids is None
            else {
                int(department_id)
                for department_id in department_ids
            }
        )

        planned_workloads = list(
            cls._planned_workloads_queryset(
                academic_year=academic_year,
                department_ids=normalized_department_ids,
            )
        )

        distributions = list(
            cls._distributions_queryset(
                academic_year=academic_year,
                department_ids=normalized_department_ids,
            )
        )

        year_records = list(
            cls._year_records_queryset(
                academic_year=academic_year,
                department_ids=normalized_department_ids,
            )
        )

        issues = []

        issues.extend(
            cls._validate_planned_workloads(
                planned_workloads=planned_workloads,
            )
        )
        issues.extend(
            cls._validate_distributions(
                distributions=distributions,
                academic_year=academic_year,
            )
        )
        issues.extend(
            cls._validate_teacher_norms(
                year_records=year_records,
                distributions=distributions,
            )
        )

        issues = cls._apply_issue_filters(
            issues=issues,
            severity=severity,
            issue_type=issue_type,
        )

        issues.sort(
            key=lambda item: (
                cls._severity_sort_order(
                    item["severity"]
                ),
                item["issue_type"],
                item.get("department_name") or "",
                item.get("teacher_name") or "",
                item.get("planned_workload_id") or 0,
                item.get("distribution_id") or 0,
            )
        )

        summary = cls._build_summary(
            planned_workloads=planned_workloads,
            distributions=distributions,
            year_records=year_records,
            issues=issues,
        )

        return {
            "academic_year": academic_year.pk,
            "academic_year_name": academic_year.name,
            "department_ids": (
                sorted(normalized_department_ids)
                if normalized_department_ids is not None
                else []
            ),
            "is_valid": summary["errors_count"] == 0,
            "summary": summary,
            "issues": issues,
        }

    @classmethod
    def _planned_workloads_queryset(
        cls,
        *,
        academic_year,
        department_ids,
    ):
        decimal_output = DecimalField(
            max_digits=14,
            decimal_places=2,
        )

        queryset = (
            PlannedWorkload.objects
            .filter(
                academic_year=academic_year,
                is_archived=False,
            )
            .select_related(
                "academic_year",
                "academic_semester",
                "teaching_department",
                "teaching_stream",
                "teaching_stream__curriculum_discipline",
                "teaching_stream__curriculum_discipline__discipline",
                "curriculum_workload",
                "curriculum_workload__workload_type",
            )
            .annotate(
                draft_hours=Coalesce(
                    Sum(
                        "distributions__allocated_hours",
                        filter=Q(
                            distributions__is_archived=False,
                            distributions__status=(
                                WorkloadDistribution.Status.DRAFT
                            ),
                        ),
                    ),
                    Value(
                        Decimal("0.00"),
                        output_field=decimal_output,
                    ),
                ),
                approved_hours=Coalesce(
                    Sum(
                        "distributions__allocated_hours",
                        filter=Q(
                            distributions__is_archived=False,
                            distributions__status=(
                                WorkloadDistribution.Status.APPROVED
                            ),
                        ),
                    ),
                    Value(
                        Decimal("0.00"),
                        output_field=decimal_output,
                    ),
                ),
            )
            .annotate(
                active_distributed_hours=(
                    F("draft_hours")
                    + F("approved_hours")
                )
            )
            .order_by(
                "teaching_department__name_ru",
                "teaching_stream__code",
            )
        )

        if department_ids is not None:
            queryset = queryset.filter(
                teaching_department_id__in=(
                    department_ids
                )
            )

        return queryset

    @classmethod
    def _distributions_queryset(
        cls,
        *,
        academic_year,
        department_ids,
    ):
        queryset = (
            WorkloadDistribution.objects
            .filter(
                planned_workload__academic_year=academic_year,
                is_archived=False,
            )
            .select_related(
                "planned_workload",
                "planned_workload__academic_year",
                "planned_workload__academic_semester",
                "planned_workload__teaching_department",
                "planned_workload__teaching_stream",
                "planned_workload__teaching_stream__curriculum_discipline",
                "planned_workload__teaching_stream__curriculum_discipline__discipline",
                "planned_workload__curriculum_workload",
                "planned_workload__curriculum_workload__workload_type",
                "staff_employment",
                "staff_employment__staff_member",
                "staff_employment__position",
                "staff_employment__department",
                "approved_by",
            )
            .order_by(
                "planned_workload__teaching_department__name_ru",
                "staff_employment__staff_member__last_name",
                "pk",
            )
        )

        if department_ids is not None:
            queryset = queryset.filter(
                planned_workload__teaching_department_id__in=(
                    department_ids
                )
            )

        return queryset

    @classmethod
    def _year_records_queryset(
        cls,
        *,
        academic_year,
        department_ids,
    ):
        queryset = (
            StaffEmploymentAcademicYear.objects
            .filter(
                academic_year=academic_year,
                is_archived=False,
                is_active=True,
                staff_employment__is_archived=False,
                staff_employment__position__is_teaching_position=True,
            )
            .select_related(
                "academic_year",
                "staff_employment",
                "staff_employment__staff_member",
                "staff_employment__position",
                "staff_employment__department",
                "academic_degree",
                "academic_title",
            )
            .order_by(
                "staff_employment__department__name_ru",
                "staff_employment__staff_member__last_name",
            )
        )

        if department_ids is not None:
            queryset = queryset.filter(
                staff_employment__department_id__in=(
                    department_ids
                )
            )

        return queryset

    @classmethod
    def _validate_planned_workloads(
        cls,
        *,
        planned_workloads,
    ) -> list:
        issues = []

        for planned_workload in planned_workloads:
            if (
                planned_workload.status
                == PlannedWorkload.Status.CANCELLED
            ):
                continue

            total_hours = cls._decimal(
                planned_workload.total_hours
            )
            distributed_hours = cls._decimal(
                planned_workload.active_distributed_hours
            )
            remaining_hours = (
                total_hours - distributed_hours
            ).quantize(Decimal("0.01"))

            common = cls._planned_issue_context(
                planned_workload
            )

            if distributed_hours == Decimal("0.00"):
                issues.append(
                    cls._issue(
                        severity=cls.Severity.ERROR,
                        issue_type=(
                            cls.IssueType
                            .PLANNED_WITHOUT_DISTRIBUTIONS
                        ),
                        message=(
                            "Плановая нагрузка не распределена "
                            "ни одному преподавателю."
                        ),
                        details={
                            "planned_hours": str(total_hours),
                            "distributed_hours": "0.00",
                            "remaining_hours": str(
                                remaining_hours
                            ),
                        },
                        **common,
                    )
                )

            elif distributed_hours < total_hours:
                issues.append(
                    cls._issue(
                        severity=cls.Severity.WARNING,
                        issue_type=(
                            cls.IssueType
                            .PLANNED_PARTIALLY_DISTRIBUTED
                        ),
                        message=(
                            "Плановая нагрузка распределена "
                            "не полностью."
                        ),
                        details={
                            "planned_hours": str(total_hours),
                            "distributed_hours": str(
                                distributed_hours
                            ),
                            "remaining_hours": str(
                                remaining_hours
                            ),
                        },
                        **common,
                    )
                )

            elif distributed_hours > total_hours:
                exceeded_hours = (
                    distributed_hours - total_hours
                ).quantize(Decimal("0.01"))

                issues.append(
                    cls._issue(
                        severity=cls.Severity.ERROR,
                        issue_type=(
                            cls.IssueType
                            .PLANNED_HOURS_EXCEEDED
                        ),
                        message=(
                            "Сумма активных распределений "
                            "превышает плановые часы."
                        ),
                        details={
                            "planned_hours": str(total_hours),
                            "distributed_hours": str(
                                distributed_hours
                            ),
                            "exceeded_hours": str(
                                exceeded_hours
                            ),
                        },
                        **common,
                    )
                )

            expected_status = (
                cls._expected_planned_status(
                    total_hours=total_hours,
                    distributed_hours=distributed_hours,
                )
            )

            if planned_workload.status != expected_status:
                issues.append(
                    cls._issue(
                        severity=cls.Severity.ERROR,
                        issue_type=(
                            cls.IssueType
                            .PLANNED_STATUS_MISMATCH
                        ),
                        message=(
                            "Статус плановой нагрузки "
                            "не соответствует фактически "
                            "распределённым часам."
                        ),
                        details={
                            "current_status": (
                                planned_workload.status
                            ),
                            "current_status_label": (
                                planned_workload
                                .get_status_display()
                            ),
                            "expected_status": (
                                expected_status
                            ),
                            "planned_hours": str(total_hours),
                            "distributed_hours": str(
                                distributed_hours
                            ),
                        },
                        **common,
                    )
                )

        return issues

    @classmethod
    def _validate_distributions(
        cls,
        *,
        distributions,
        academic_year,
    ) -> list:
        issues = []

        active_year_record_keys = set(
            StaffEmploymentAcademicYear.objects
            .filter(
                academic_year=academic_year,
                is_archived=False,
                is_active=True,
            )
            .values_list(
                "staff_employment_id",
                "academic_year_id",
            )
        )

        for distribution in distributions:
            common = cls._distribution_issue_context(
                distribution
            )

            if (
                distribution.status
                == WorkloadDistribution.Status.DRAFT
            ):
                issues.append(
                    cls._issue(
                        severity=cls.Severity.WARNING,
                        issue_type=(
                            cls.IssueType.DISTRIBUTION_DRAFT
                        ),
                        message=(
                            "Распределение находится "
                            "в статусе черновика."
                        ),
                        details={
                            "allocated_hours": str(
                                cls._decimal(
                                    distribution.allocated_hours
                                )
                            ),
                        },
                        **common,
                    )
                )

            cls._append_approval_issues(
                issues=issues,
                distribution=distribution,
                common=common,
            )

            employment = distribution.staff_employment

            if employment.is_archived:
                issues.append(
                    cls._issue(
                        severity=cls.Severity.ERROR,
                        issue_type=(
                            cls.IssueType.EMPLOYMENT_ARCHIVED
                        ),
                        message=(
                            "Распределение связано с архивным "
                            "трудовым назначением."
                        ),
                        details={},
                        **common,
                    )
                )

            if not employment.is_active:
                issues.append(
                    cls._issue(
                        severity=cls.Severity.ERROR,
                        issue_type=(
                            cls.IssueType.EMPLOYMENT_INACTIVE
                        ),
                        message=(
                            "Распределение связано с неактивным "
                            "трудовым назначением."
                        ),
                        details={},
                        **common,
                    )
                )

            if not employment.position.is_teaching_position:
                issues.append(
                    cls._issue(
                        severity=cls.Severity.ERROR,
                        issue_type=(
                            cls.IssueType.NON_TEACHING_POSITION
                        ),
                        message=(
                            "Нагрузка распределена на должность, "
                            "которая не участвует в учебной работе."
                        ),
                        details={
                            "position_id": (
                                employment.position_id
                            ),
                            "position_name": (
                                employment.position.name_ru
                            ),
                        },
                        **common,
                    )
                )

            if (
                employment.department_id
                != distribution.planned_workload
                .teaching_department_id
            ):
                issues.append(
                    cls._issue(
                        severity=cls.Severity.ERROR,
                        issue_type=(
                            cls.IssueType
                            .EMPLOYMENT_DEPARTMENT_MISMATCH
                        ),
                        message=(
                            "Кафедра трудового назначения "
                            "не совпадает с кафедрой "
                            "плановой нагрузки."
                        ),
                        details={
                            "employment_department_id": (
                                employment.department_id
                            ),
                            "employment_department_name": (
                                employment.department.name_ru
                            ),
                            "planned_department_id": (
                                distribution.planned_workload
                                .teaching_department_id
                            ),
                            "planned_department_name": (
                                distribution.planned_workload
                                .teaching_department.name_ru
                            ),
                        },
                        **common,
                    )
                )

            year_record_key = (
                employment.pk,
                academic_year.pk,
            )

            if (
                year_record_key
                not in active_year_record_keys
            ):
                issues.append(
                    cls._issue(
                        severity=cls.Severity.ERROR,
                        issue_type=(
                            cls.IssueType
                            .YEAR_STAFF_RECORD_MISSING
                        ),
                        message=(
                            "Для трудового назначения отсутствует "
                            "активная кадровая запись "
                            "на выбранный учебный год."
                        ),
                        details={
                            "staff_employment_id": (
                                employment.pk
                            ),
                            "academic_year_id": (
                                academic_year.pk
                            ),
                        },
                        **common,
                    )
                )

        return issues

    @classmethod
    def _append_approval_issues(
        cls,
        *,
        issues,
        distribution,
        common,
    ):
        is_approved = (
            distribution.status
            == WorkloadDistribution.Status.APPROVED
        )

        if (
            is_approved
            and (
                distribution.approved_at is None
                or distribution.approved_by_id is None
            )
        ):
            issues.append(
                cls._issue(
                    severity=cls.Severity.ERROR,
                    issue_type=(
                        cls.IssueType.APPROVAL_DATA_MISSING
                    ),
                    message=(
                        "Утверждённое распределение не содержит "
                        "полных данных об утверждении."
                    ),
                    details={
                        "approved_at_present": (
                            distribution.approved_at
                            is not None
                        ),
                        "approved_by_present": (
                            distribution.approved_by_id
                            is not None
                        ),
                    },
                    **common,
                )
            )

        if (
            not is_approved
            and (
                distribution.approved_at is not None
                or distribution.approved_by_id is not None
            )
        ):
            issues.append(
                cls._issue(
                    severity=cls.Severity.ERROR,
                    issue_type=(
                        cls.IssueType
                        .APPROVAL_DATA_UNEXPECTED
                    ),
                    message=(
                        "Неутверждённое распределение содержит "
                        "данные об утверждении."
                    ),
                    details={
                        "approved_at": (
                            distribution.approved_at.isoformat()
                            if distribution.approved_at
                            else None
                        ),
                        "approved_by_id": (
                            distribution.approved_by_id
                        ),
                    },
                    **common,
                )
            )

    @classmethod
    def _validate_teacher_norms(
        cls,
        *,
        year_records,
        distributions,
    ) -> list:
        issues = []

        distributed_hours_by_employment = defaultdict(
            lambda: Decimal("0.00")
        )

        for distribution in distributions:
            if (
                distribution.status
                not in cls.ACTIVE_DISTRIBUTION_STATUSES
            ):
                continue

            distributed_hours_by_employment[
                distribution.staff_employment_id
            ] += cls._decimal(
                distribution.allocated_hours
            )

        for year_record in year_records:
            employment = year_record.staff_employment
            distributed_hours = (
                distributed_hours_by_employment[
                    employment.pk
                ]
            ).quantize(Decimal("0.01"))

            norm = year_record.get_workload_norm()

            common = {
                "department_id": (
                    employment.department_id
                ),
                "department_name": (
                    employment.department.name_ru
                ),
                "staff_employment_id": employment.pk,
                "staff_member_id": (
                    employment.staff_member_id
                ),
                "teacher_name": (
                    employment.staff_member.full_name
                ),
                "planned_workload_id": None,
                "distribution_id": None,
            }

            if norm is None:
                issues.append(
                    cls._issue(
                        severity=cls.Severity.WARNING,
                        issue_type=(
                            cls.IssueType.WORKLOAD_NORM_MISSING
                        ),
                        message=(
                            "Для кадрового состояния преподавателя "
                            "не найдена действующая норма нагрузки."
                        ),
                        details={
                            "year_staff_record_id": (
                                year_record.pk
                            ),
                            "rate": str(
                                cls._decimal(
                                    year_record.rate
                                )
                            ),
                            "has_academic_degree": (
                                year_record
                                .has_academic_degree
                            ),
                            "has_academic_title": (
                                year_record
                                .has_academic_title
                            ),
                            "distributed_hours": str(
                                distributed_hours
                            ),
                        },
                        **common,
                    )
                )
                continue

            recommended_hours = cls._decimal(
                norm.annual_hours
            )

            if distributed_hours > recommended_hours:
                overload_hours = (
                    distributed_hours
                    - recommended_hours
                ).quantize(Decimal("0.01"))

                load_percent = cls._percent(
                    distributed_hours,
                    recommended_hours,
                )

                issues.append(
                    cls._issue(
                        severity=cls.Severity.WARNING,
                        issue_type=(
                            cls.IssueType.TEACHER_OVERLOADED
                        ),
                        message=(
                            "Распределённая нагрузка превышает "
                            "рекомендуемую годовую норму."
                        ),
                        details={
                            "year_staff_record_id": (
                                year_record.pk
                            ),
                            "workload_norm_id": norm.pk,
                            "recommended_hours": str(
                                recommended_hours
                            ),
                            "distributed_hours": str(
                                distributed_hours
                            ),
                            "overload_hours": str(
                                overload_hours
                            ),
                            "load_percent": str(
                                load_percent
                            ),
                        },
                        **common,
                    )
                )

        return issues

    @classmethod
    def _expected_planned_status(
        cls,
        *,
        total_hours,
        distributed_hours,
    ):
        if distributed_hours == Decimal("0.00"):
            state = "empty"
        elif distributed_hours < total_hours:
            state = "partial"
        elif distributed_hours == total_hours:
            state = "full"
        else:
            state = "exceeded"

        return cls.EXPECTED_PLANNED_STATUS_BY_STATE[
            state
        ]

    @staticmethod
    def _planned_issue_context(
        planned_workload,
    ) -> dict:
        return {
            "department_id": (
                planned_workload.teaching_department_id
            ),
            "department_name": (
                planned_workload
                .teaching_department.name_ru
            ),
            "staff_employment_id": None,
            "staff_member_id": None,
            "teacher_name": None,
            "planned_workload_id": (
                planned_workload.pk
            ),
            "distribution_id": None,
            "stream_code": (
                planned_workload.teaching_stream.code
            ),
            "discipline_name": (
                planned_workload
                .teaching_stream
                .curriculum_discipline
                .discipline
                .name_ru
            ),
            "workload_type_name": (
                planned_workload
                .curriculum_workload
                .workload_type
                .name_ru
            ),
        }

    @staticmethod
    def _distribution_issue_context(
        distribution,
    ) -> dict:
        planned_workload = distribution.planned_workload
        employment = distribution.staff_employment

        return {
            "department_id": (
                planned_workload.teaching_department_id
            ),
            "department_name": (
                planned_workload
                .teaching_department.name_ru
            ),
            "staff_employment_id": employment.pk,
            "staff_member_id": (
                employment.staff_member_id
            ),
            "teacher_name": (
                employment.staff_member.full_name
            ),
            "planned_workload_id": (
                planned_workload.pk
            ),
            "distribution_id": distribution.pk,
            "stream_code": (
                planned_workload.teaching_stream.code
            ),
            "discipline_name": (
                planned_workload
                .teaching_stream
                .curriculum_discipline
                .discipline
                .name_ru
            ),
            "workload_type_name": (
                planned_workload
                .curriculum_workload
                .workload_type
                .name_ru
            ),
        }

    @staticmethod
    def _issue(
        *,
        severity,
        issue_type,
        message,
        details,
        department_id,
        department_name,
        staff_employment_id,
        staff_member_id,
        teacher_name,
        planned_workload_id,
        distribution_id,
        stream_code=None,
        discipline_name=None,
        workload_type_name=None,
    ) -> dict:
        return {
            "severity": severity,
            "issue_type": issue_type,
            "message": message,
            "department_id": department_id,
            "department_name": department_name,
            "staff_employment_id": (
                staff_employment_id
            ),
            "staff_member_id": staff_member_id,
            "teacher_name": teacher_name,
            "planned_workload_id": (
                planned_workload_id
            ),
            "distribution_id": distribution_id,
            "stream_code": stream_code,
            "discipline_name": discipline_name,
            "workload_type_name": (
                workload_type_name
            ),
            "details": details,
        }

    @classmethod
    def _build_summary(
        cls,
        *,
        planned_workloads,
        distributions,
        year_records,
        issues,
    ) -> dict:
        errors_count = sum(
            1
            for issue in issues
            if issue["severity"]
            == cls.Severity.ERROR
        )
        warnings_count = sum(
            1
            for issue in issues
            if issue["severity"]
            == cls.Severity.WARNING
        )

        issues_by_type = defaultdict(int)

        for issue in issues:
            issues_by_type[issue["issue_type"]] += 1

        return {
            "planned_workloads_count": len(
                planned_workloads
            ),
            "distributions_count": len(
                distributions
            ),
            "year_staff_records_count": len(
                year_records
            ),
            "issues_count": len(issues),
            "errors_count": errors_count,
            "warnings_count": warnings_count,
            "issues_by_type": dict(
                sorted(issues_by_type.items())
            ),
        }

    @classmethod
    def _apply_issue_filters(
        cls,
        *,
        issues,
        severity,
        issue_type,
    ) -> list:
        result = issues

        if severity:
            result = [
                issue
                for issue in result
                if issue["severity"] == severity
            ]

        if issue_type:
            result = [
                issue
                for issue in result
                if issue["issue_type"] == issue_type
            ]

        return result

    @classmethod
    def _validate_filters(
        cls,
        *,
        severity,
        issue_type,
    ):
        if (
            severity
            and severity not in cls.Severity.CHOICES
        ):
            raise ValueError(
                "Неизвестный уровень серьёзности."
            )

        if (
            issue_type
            and issue_type not in cls.IssueType.CHOICES
        ):
            raise ValueError(
                "Неизвестный тип проблемы."
            )

    @staticmethod
    def _severity_sort_order(severity):
        return {
            AcademicYearWorkloadValidationService
            .Severity.ERROR: 0,
            AcademicYearWorkloadValidationService
            .Severity.WARNING: 1,
        }.get(severity, 99)

    @staticmethod
    def _decimal(value) -> Decimal:
        return Decimal(
            str(value or "0.00")
        ).quantize(Decimal("0.01"))

    @staticmethod
    def _percent(
        value,
        base,
    ) -> Decimal:
        if not base:
            return Decimal("0.00")

        return (
            Decimal(str(value))
            / Decimal(str(base))
            * Decimal("100.00")
        ).quantize(Decimal("0.01"))