from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from django.db.models import (
    Q,
    Sum,
)

from apps.staff.models import StaffEmployment
from apps.workload.models import (
    WorkloadDistribution,
)


ZERO = Decimal("0.00")


class TeacherLoadSummaryService:
    """
    Расчёт итоговой нагрузки преподавателей
    за учебный год.

    Важно:

    DRAFT:
        показывается отдельно и не входит
        в официально утверждённую нагрузку.

    APPROVED:
        входит в итоговую нагрузку.

    CANCELLED / ARCHIVED:
        не учитываются.
    """

    @classmethod
    def build_for_employment(
        cls,
        *,
        staff_employment: StaffEmployment,
        academic_year_id: int,
    ) -> dict:
        distributions = (
            WorkloadDistribution.objects
            .filter(
                staff_employment=staff_employment,
                planned_workload__academic_year_id=(
                    academic_year_id
                ),
                is_archived=False,
            )
            .select_related(
                "planned_workload",
                "planned_workload__curriculum_workload",
                (
                    "planned_workload__"
                    "curriculum_workload__"
                    "workload_type"
                ),
            )
        )

        approved_hours = ZERO
        draft_hours = ZERO
        cancelled_hours = ZERO

        approved_count = 0
        draft_count = 0
        cancelled_count = 0

        for distribution in distributions:
            hours = (
                distribution.allocated_hours
                or ZERO
            )

            if (
                distribution.status
                == WorkloadDistribution.Status.APPROVED
            ):
                approved_hours += hours
                approved_count += 1

            elif (
                distribution.status
                == WorkloadDistribution.Status.DRAFT
            ):
                draft_hours += hours
                draft_count += 1

            elif (
                distribution.status
                == WorkloadDistribution.Status.CANCELLED
            ):
                cancelled_hours += hours
                cancelled_count += 1

        annual_norm = (
            cls._get_annual_norm(
                staff_employment=staff_employment,
                academic_year_id=academic_year_id,
            )
        )

        remaining = (
            annual_norm -
            approved_hours
        )

        percentage = (
            (
                approved_hours /
                annual_norm
            ) * Decimal("100")
            if annual_norm > ZERO
            else ZERO
        )

        if approved_hours > annual_norm:
            status = "OVERLOAD"

        elif approved_hours == annual_norm:
            status = "FULL"

        else:
            status = "UNDERLOAD"

        return {
            "staff_employment": (
                staff_employment.pk
            ),
            "staff_member": (
                staff_employment
                .staff_member_id
            ),
            "staff_member_name": str(
                staff_employment
                .staff_member
            ),
            "department": (
                staff_employment
                .department_id
            ),
            "annual_norm_hours": (
                annual_norm
            ),
            "approved_hours": (
                approved_hours
            ),
            "draft_hours": (
                draft_hours
            ),
            "remaining_hours": (
                remaining
            ),
            "completion_percent": (
                percentage.quantize(
                    Decimal("0.01")
                )
            ),
            "approved_count": (
                approved_count
            ),
            "draft_count": (
                draft_count
            ),
            "cancelled_count": (
                cancelled_count
            ),
            "status": status,
        }

    @classmethod
    def _get_annual_norm(
        cls,
        *,
        staff_employment,
        academic_year_id,
    ) -> Decimal:
        """
        Получает индивидуальную годовую норму.

        Если в StaffEmployment нет индивидуальной
        нормы, используется годовая норма кафедры/
        должности через существующую модель норм.

        Метод намеренно изолирован, чтобы не
        размазывать правила определения нормы
        по API и frontend.
        """

        record = (
            staff_employment
            .academic_year_records
            .filter(
                academic_year_id=academic_year_id,
                is_active=True,
                is_archived=False,
            )
            .first()
        )

        if record is None:
            return ZERO

        recommended_hours = (
            record.get_recommended_annual_hours()
        )

        if recommended_hours is None:
            return ZERO

        return recommended_hours

    @classmethod
    def build_for_department(
        cls,
        *,
        department_id: int,
        academic_year_id: int,
    ) -> list[dict]:
        employments = (
            StaffEmployment.objects
            .filter(
                department_id=department_id,
                is_active=True,
                is_archived=False,
            )
            .select_related(
                "staff_member",
                "department",
            )
            .prefetch_related(
                "academic_year_records",
            )
            .order_by(
                "staff_member__last_name",
                "staff_member__first_name",
                "pk",
            )
        )

        return [
            cls.build_for_employment(
                staff_employment=employment,
                academic_year_id=academic_year_id,
            )
            for employment in employments
        ]