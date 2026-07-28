from collections import Counter
from decimal import Decimal

from apps.workload.services.department_workload_service import (
    DepartmentWorkloadService,
)
from apps.workload.services.teacher_workload_service import (
    TeacherWorkloadService,
)


class WorkloadDashboardService:
    ZERO = Decimal("0.00")
    QUANTIZER = Decimal("0.01")

    @classmethod
    def get_dashboard(
        cls,
        *,
        academic_year,
        department_id=None,
        allowed_department_ids=None,
        allowed_staff_member_ids=None,
    ) -> dict:
        department_summary = (
            DepartmentWorkloadService.get_summary(
                academic_year=academic_year,
                department_id=department_id,
                allowed_department_ids=(
                    allowed_department_ids
                ),
            )
        )

        teacher_summary = (
            TeacherWorkloadService.get_summary(
                academic_year=academic_year,
                department_id=department_id,
                allowed_department_ids=(
                    allowed_department_ids
                ),
                allowed_staff_member_ids=(
                    allowed_staff_member_ids
                ),
            )
        )

        planned_positions = sum(
            (
                item["planned_positions"]
                for item in department_summary
            ),
            0,
        )

        planned_hours = cls._sum_decimal(
            department_summary,
            "planned_hours",
        )
        draft_hours = cls._sum_decimal(
            department_summary,
            "draft_hours",
        )
        approved_hours = cls._sum_decimal(
            department_summary,
            "approved_hours",
        )
        distributed_hours = cls._sum_decimal(
            department_summary,
            "distributed_hours",
        )
        remaining_hours = cls._sum_decimal(
            department_summary,
            "remaining_hours",
        )

        if planned_hours > cls.ZERO:
            distribution_percent = (
                distributed_hours
                / planned_hours
                * Decimal("100.00")
            ).quantize(cls.QUANTIZER)
        else:
            distribution_percent = cls.ZERO

        teacher_statuses = Counter(
            item["load_status"]
            for item in teacher_summary
        )

        department_statuses = Counter(
            item["distribution_status"]
            for item in department_summary
        )

        recommended_teacher_hours = (
            cls._sum_optional_decimal(
                teacher_summary,
                "recommended_hours",
            )
        )
        distributed_teacher_hours = cls._sum_decimal(
            teacher_summary,
            "distributed_hours",
        )

        teacher_norm_count = sum(
            1
            for item in teacher_summary
            if item["norm_found"]
        )

        return {
            "academic_year": academic_year.id,
            "academic_year_name": academic_year.name,
            "department": (
                int(department_id)
                if department_id
                else None
            ),
            "workload": {
                "planned_positions": planned_positions,
                "planned_hours": planned_hours,
                "draft_hours": draft_hours,
                "approved_hours": approved_hours,
                "distributed_hours": distributed_hours,
                "remaining_hours": remaining_hours,
                "distribution_percent": (
                    distribution_percent
                ),
            },
            "teachers": {
                "total": len(teacher_summary),
                "with_norm": teacher_norm_count,
                "without_norm": teacher_statuses[
                    "norm_missing"
                ],
                "underloaded": teacher_statuses[
                    "underloaded"
                ],
                "balanced": teacher_statuses[
                    "balanced"
                ],
                "overloaded": teacher_statuses[
                    "overloaded"
                ],
                "recommended_hours": (
                    recommended_teacher_hours
                ),
                "distributed_hours": (
                    distributed_teacher_hours
                ),
            },
            "departments": {
                "total": len(department_summary),
                "incomplete": department_statuses[
                    "incomplete"
                ],
                "complete": department_statuses[
                    "complete"
                ],
                "exceeded": department_statuses[
                    "exceeded"
                ],
            },
        }

    @classmethod
    def _sum_decimal(
        cls,
        items,
        field_name,
    ) -> Decimal:
        return sum(
            (
                item.get(field_name) or cls.ZERO
                for item in items
            ),
            cls.ZERO,
        ).quantize(cls.QUANTIZER)

    @classmethod
    def _sum_optional_decimal(
        cls,
        items,
        field_name,
    ) -> Decimal:
        return sum(
            (
                item[field_name]
                for item in items
                if item.get(field_name) is not None
            ),
            cls.ZERO,
        ).quantize(cls.QUANTIZER)