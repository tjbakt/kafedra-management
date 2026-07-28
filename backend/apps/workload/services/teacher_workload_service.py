from decimal import Decimal

from django.db.models import Q, Sum

from apps.staff.models import StaffEmploymentAcademicYear
from apps.workload.models import WorkloadDistribution


class TeacherWorkloadService:
    ACTIVE_DISTRIBUTION_STATUSES = (
        WorkloadDistribution.Status.DRAFT,
        WorkloadDistribution.Status.APPROVED,
    )

    @classmethod
    def get_summary(
        cls,
        *,
        academic_year,
        staff_member_id=None,
        department_id=None,
        allowed_department_ids=None,
        allowed_staff_member_ids=None,
    ) -> list[dict]:
        year_records = (
            StaffEmploymentAcademicYear.objects
            .select_related(
                "academic_year",
                "academic_degree",
                "academic_title",
                "staff_employment",
                "staff_employment__staff_member",
                "staff_employment__department",
                "staff_employment__position",
            )
            .filter(
                academic_year=academic_year,
                is_active=True,
                is_archived=False,
                staff_employment__is_archived=False,
                staff_employment__position__is_teaching_position=True,
            )
            .order_by(
                "staff_employment__staff_member__last_name",
                "staff_employment__staff_member__first_name",
            )
        )

        if staff_member_id:
            year_records = year_records.filter(
                staff_employment__staff_member_id=staff_member_id
            )

        if department_id:
            year_records = year_records.filter(
                staff_employment__department_id=department_id
            )

        year_records = cls._apply_access_scope(
            queryset=year_records,
            allowed_department_ids=allowed_department_ids,
            allowed_staff_member_ids=allowed_staff_member_ids,
        )

        result = []

        for year_record in year_records:
            employment = year_record.staff_employment
            staff_member = employment.staff_member

            distributed_hours = (
                WorkloadDistribution.objects
                .filter(
                    staff_employment=employment,
                    planned_workload__academic_year=academic_year,
                    status__in=cls.ACTIVE_DISTRIBUTION_STATUSES,
                    is_archived=False,
                )
                .aggregate(total=Sum("allocated_hours"))["total"]
                or Decimal("0.00")
            ).quantize(Decimal("0.01"))

            norm = year_record.get_workload_norm()
            recommended_hours = (
                norm.annual_hours
                if norm is not None
                else None
            )

            if recommended_hours is None:
                remaining_hours = None
                difference_hours = None
                load_percent = None
                load_status = "norm_missing"
            else:
                recommended_hours = recommended_hours.quantize(
                    Decimal("0.01")
                )

                remaining_hours = (
                    recommended_hours - distributed_hours
                ).quantize(Decimal("0.01"))

                difference_hours = (
                    distributed_hours - recommended_hours
                ).quantize(Decimal("0.01"))

                if recommended_hours > Decimal("0.00"):
                    load_percent = (
                        distributed_hours
                        / recommended_hours
                        * Decimal("100.00")
                    ).quantize(Decimal("0.01"))
                else:
                    load_percent = None

                if distributed_hours < recommended_hours:
                    load_status = "underloaded"
                elif distributed_hours > recommended_hours:
                    load_status = "overloaded"
                else:
                    load_status = "balanced"

            result.append(
                {
                    "staff_employment_academic_year": (
                        year_record.id
                    ),
                    "staff_employment": employment.id,
                    "staff_member": staff_member.id,
                    "teacher_name": staff_member.full_name,
                    "personnel_number": (
                        staff_member.personnel_number
                    ),
                    "department": employment.department_id,
                    "department_name": (
                        employment.department.name_ru
                    ),
                    "position": employment.position_id,
                    "position_name": employment.position.name_ru,
                    "academic_year": academic_year.id,
                    "academic_year_name": academic_year.name,
                    "employment_rate": year_record.rate,
                    "has_academic_degree": (
                        year_record.has_academic_degree
                    ),
                    "has_academic_title": (
                        year_record.has_academic_title
                    ),
                    "recommended_hours": recommended_hours,
                    "distributed_hours": distributed_hours,
                    "remaining_hours": remaining_hours,
                    "difference_hours": difference_hours,
                    "load_percent": load_percent,
                    "load_status": load_status,
                    "norm_found": norm is not None,
                }
            )

        return result

    @classmethod
    def _apply_access_scope(
            cls,
            *,
            queryset,
            allowed_department_ids,
            allowed_staff_member_ids,
    ):
        """
        Применяет объединённую область доступа.

        Заведующий видит преподавателей доступной кафедры.
        Преподаватель видит собственную запись.
        При наличии обеих ролей условия объединяются через OR.
        """

        if (
                allowed_department_ids is None
                and allowed_staff_member_ids is None
        ):
            return queryset

        access_filter = Q(pk__in=[])

        if allowed_department_ids:
            access_filter |= Q(
                staff_employment__department_id__in=(
                    allowed_department_ids
                )
            )

        if allowed_staff_member_ids:
            access_filter |= Q(
                staff_employment__staff_member_id__in=(
                    allowed_staff_member_ids
                )
            )

        return queryset.filter(access_filter)