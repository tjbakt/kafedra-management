from decimal import Decimal

from django.db.models import (
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    Q,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce

from apps.workload.models import (
    PlannedWorkload,
    WorkloadDistribution,
)


class DepartmentWorkloadService:
    DECIMAL_FIELD = DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    @classmethod
    def get_summary(
        cls,
        *,
        academic_year,
        academic_semester_id=None,
        department_id=None,
        allowed_department_ids=None,
    ) -> list[dict]:
        queryset = (
            PlannedWorkload.objects
            .filter(
                academic_year=academic_year,
                is_archived=False,
            )
        )

        if academic_semester_id:
            queryset = queryset.filter(
                academic_semester_id=academic_semester_id,
            )

        if department_id:
            queryset = queryset.filter(
                teaching_department_id=department_id,
            )

        if allowed_department_ids is not None:
            queryset = queryset.filter(
                teaching_department_id__in=(
                    allowed_department_ids
                ),
            )

        zero = Value(
            Decimal("0.00"),
            output_field=cls.DECIMAL_FIELD,
        )

        queryset = (
            queryset
            .values(
                "teaching_department_id",
                "teaching_department__name_ru",
            )
            .annotate(
                planned_positions=Count(
                    "id",
                    distinct=True,
                ),
                planned_hours=Coalesce(
                    Sum("total_hours"),
                    zero,
                    output_field=cls.DECIMAL_FIELD,
                ),
                draft_hours=Coalesce(
                    Sum(
                        "distributions__allocated_hours",
                        filter=Q(
                            distributions__status=(
                                WorkloadDistribution.Status.DRAFT
                            ),
                            distributions__is_archived=False,
                        ),
                    ),
                    zero,
                    output_field=cls.DECIMAL_FIELD,
                ),
                approved_hours=Coalesce(
                    Sum(
                        "distributions__allocated_hours",
                        filter=Q(
                            distributions__status=(
                                WorkloadDistribution.Status.APPROVED
                            ),
                            distributions__is_archived=False,
                        ),
                    ),
                    zero,
                    output_field=cls.DECIMAL_FIELD,
                ),
            )
            .annotate(
                distributed_hours=ExpressionWrapper(
                    F("draft_hours") + F("approved_hours"),
                    output_field=cls.DECIMAL_FIELD,
                )
            )
            .annotate(
                remaining_hours=ExpressionWrapper(
                    F("planned_hours")
                    - F("distributed_hours"),
                    output_field=cls.DECIMAL_FIELD,
                )
            )
            .order_by(
                "teaching_department__name_ru"
            )
        )

        result = []

        for item in queryset:
            planned_hours = (
                item["planned_hours"]
                or Decimal("0.00")
            )
            distributed_hours = (
                item["distributed_hours"]
                or Decimal("0.00")
            )

            if planned_hours > Decimal("0.00"):
                distribution_percent = (
                    distributed_hours
                    / planned_hours
                    * Decimal("100.00")
                ).quantize(Decimal("0.01"))
            else:
                distribution_percent = Decimal("0.00")

            remaining_hours = (
                item["remaining_hours"]
                or Decimal("0.00")
            )

            if remaining_hours > Decimal("0.00"):
                distribution_status = "incomplete"
            elif remaining_hours < Decimal("0.00"):
                distribution_status = "exceeded"
            else:
                distribution_status = "complete"

            result.append(
                {
                    "department": (
                        item["teaching_department_id"]
                    ),
                    "department_name": (
                        item[
                            "teaching_department__name_ru"
                        ]
                    ),
                    "academic_year": academic_year.id,
                    "academic_year_name": academic_year.name,
                    "planned_positions": (
                        item["planned_positions"]
                    ),
                    "planned_hours": (
                        planned_hours.quantize(
                            Decimal("0.01")
                        )
                    ),
                    "draft_hours": (
                        item["draft_hours"].quantize(
                            Decimal("0.01")
                        )
                    ),
                    "approved_hours": (
                        item["approved_hours"].quantize(
                            Decimal("0.01")
                        )
                    ),
                    "distributed_hours": (
                        distributed_hours.quantize(
                            Decimal("0.01")
                        )
                    ),
                    "remaining_hours": (
                        remaining_hours.quantize(
                            Decimal("0.01")
                        )
                    ),
                    "distribution_percent": (
                        distribution_percent
                    ),
                    "distribution_status": (
                        distribution_status
                    ),
                }
            )

        return result