from collections import defaultdict

from apps.workload.services.academic_year_validation_service import (
    AcademicYearWorkloadValidationService,
)


class AcademicYearClosingReadinessService:
    """
    Определяет готовность учебного года к закрытию.

    Сервис не изменяет данные и использует результаты
    AcademicYearWorkloadValidationService.
    """

    BLOCKING_ISSUE_TYPES = frozenset(
        {
            AcademicYearWorkloadValidationService
            .IssueType
            .PLANNED_WITHOUT_DISTRIBUTIONS,

            AcademicYearWorkloadValidationService
            .IssueType
            .PLANNED_PARTIALLY_DISTRIBUTED,

            AcademicYearWorkloadValidationService
            .IssueType
            .PLANNED_HOURS_EXCEEDED,

            AcademicYearWorkloadValidationService
            .IssueType
            .PLANNED_STATUS_MISMATCH,

            AcademicYearWorkloadValidationService
            .IssueType
            .DISTRIBUTION_DRAFT,

            AcademicYearWorkloadValidationService
            .IssueType
            .APPROVAL_DATA_MISSING,

            AcademicYearWorkloadValidationService
            .IssueType
            .APPROVAL_DATA_UNEXPECTED,

            AcademicYearWorkloadValidationService
            .IssueType
            .EMPLOYMENT_ARCHIVED,

            AcademicYearWorkloadValidationService
            .IssueType
            .EMPLOYMENT_INACTIVE,

            AcademicYearWorkloadValidationService
            .IssueType
            .NON_TEACHING_POSITION,

            AcademicYearWorkloadValidationService
            .IssueType
            .EMPLOYMENT_DEPARTMENT_MISMATCH,

            AcademicYearWorkloadValidationService
            .IssueType
            .YEAR_STAFF_RECORD_MISSING,
        }
    )

    ADVISORY_ISSUE_TYPES = frozenset(
        {
            AcademicYearWorkloadValidationService
            .IssueType
            .WORKLOAD_NORM_MISSING,

            AcademicYearWorkloadValidationService
            .IssueType
            .TEACHER_OVERLOADED,
        }
    )

    @classmethod
    def check(
        cls,
        *,
        academic_year,
        department_ids=None,
    ) -> dict:
        """
        Возвращает результат готовности учебного года
        или выбранных кафедр к закрытию.
        """

        validation_result = (
            AcademicYearWorkloadValidationService
            .validate(
                academic_year=academic_year,
                department_ids=department_ids,
            )
        )

        blocking_issues = []
        warnings = []

        for issue in validation_result["issues"]:
            if cls._is_blocking(issue):
                blocking_issues.append(
                    cls._normalize_issue(issue)
                )
            else:
                warnings.append(
                    cls._normalize_issue(issue)
                )

        blocking_by_type = cls._count_by_type(
            blocking_issues
        )
        warnings_by_type = cls._count_by_type(
            warnings
        )

        ready_to_close = not blocking_issues

        return {
            "academic_year": academic_year.pk,
            "academic_year_name": academic_year.name,
            "department_ids": (
                validation_result["department_ids"]
            ),
            "ready_to_close": ready_to_close,
            "status": (
                "ready"
                if ready_to_close
                else "not_ready"
            ),
            "message": cls._build_message(
                ready_to_close=ready_to_close,
                blocking_count=len(blocking_issues),
                warnings_count=len(warnings),
            ),
            "summary": {
                "planned_workloads_count": (
                    validation_result["summary"][
                        "planned_workloads_count"
                    ]
                ),
                "distributions_count": (
                    validation_result["summary"][
                        "distributions_count"
                    ]
                ),
                "year_staff_records_count": (
                    validation_result["summary"][
                        "year_staff_records_count"
                    ]
                ),
                "blocking_issues_count": len(
                    blocking_issues
                ),
                "warnings_count": len(warnings),
                "blocking_issues_by_type": (
                    blocking_by_type
                ),
                "warnings_by_type": warnings_by_type,
            },
            "blocking_issues": blocking_issues,
            "warnings": warnings,
        }

    @classmethod
    def ensure_ready(
        cls,
        *,
        academic_year,
        department_ids=None,
    ) -> dict:
        """
        Возвращает результат проверки.

        Метод предназначен для будущего сервиса закрытия.
        Исключение здесь намеренно не создаётся, чтобы
        сервис закрытия мог вернуть полный список причин.
        """

        return cls.check(
            academic_year=academic_year,
            department_ids=department_ids,
        )

    @classmethod
    def _is_blocking(
        cls,
        issue,
    ) -> bool:
        issue_type = issue["issue_type"]

        if issue_type in cls.BLOCKING_ISSUE_TYPES:
            return True

        if issue_type in cls.ADVISORY_ISSUE_TYPES:
            return False

        # Новые ошибки, добавленные в сервис проверки
        # в будущем, безопаснее считать блокирующими.
        return (
            issue["severity"]
            == AcademicYearWorkloadValidationService
            .Severity.ERROR
        )

    @staticmethod
    def _normalize_issue(issue) -> dict:
        """
        Создаёт независимую копию issue.

        Это защищает результат readiness от случайного
        изменения исходного validation_result.
        """

        return {
            "severity": issue["severity"],
            "issue_type": issue["issue_type"],
            "message": issue["message"],
            "department_id": issue.get(
                "department_id"
            ),
            "department_name": issue.get(
                "department_name"
            ),
            "staff_employment_id": issue.get(
                "staff_employment_id"
            ),
            "staff_member_id": issue.get(
                "staff_member_id"
            ),
            "teacher_name": issue.get(
                "teacher_name"
            ),
            "planned_workload_id": issue.get(
                "planned_workload_id"
            ),
            "distribution_id": issue.get(
                "distribution_id"
            ),
            "stream_code": issue.get(
                "stream_code"
            ),
            "discipline_name": issue.get(
                "discipline_name"
            ),
            "workload_type_name": issue.get(
                "workload_type_name"
            ),
            "details": dict(
                issue.get("details") or {}
            ),
        }

    @staticmethod
    def _count_by_type(issues) -> dict:
        result = defaultdict(int)

        for issue in issues:
            result[issue["issue_type"]] += 1

        return dict(
            sorted(result.items())
        )

    @staticmethod
    def _build_message(
        *,
        ready_to_close,
        blocking_count,
        warnings_count,
    ) -> str:
        if ready_to_close and warnings_count:
            return (
                "Учебный год готов к закрытию, "
                f"но обнаружено предупреждений: "
                f"{warnings_count}."
            )

        if ready_to_close:
            return (
                "Учебный год готов к закрытию."
            )

        return (
            "Учебный год не готов к закрытию. "
            "Необходимо устранить блокирующие "
            f"проблемы: {blocking_count}."
        )