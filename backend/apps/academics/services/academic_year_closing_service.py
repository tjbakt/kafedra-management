from django.db import transaction
from django.utils import timezone

from apps.academics.exceptions import (
    AcademicYearClosingError,
)
from apps.academics.models import AcademicYear
from apps.audit.models import AuditEvent
from apps.audit.services.audit_service import (
    AuditService,
)
from apps.workload.services.academic_year_closing_readiness_service import (
    AcademicYearClosingReadinessService,
)


class AcademicYearClosingService:
    """
    Закрытие и повторное открытие учебного года.
    """

    @classmethod
    @transaction.atomic
    def close(
        cls,
        *,
        academic_year,
        user,
        comment="",
    ) -> tuple:
        """
        Закрывает учебный год.

        Возвращает:
            (academic_year, readiness_result)
        """

        locked_year = (
            AcademicYear.objects
            .select_for_update()
            .get(pk=academic_year.pk)
        )

        if locked_year.is_archived:
            raise AcademicYearClosingError(
                "Архивный учебный год нельзя закрыть.",
                code="academic_year_archived",
            )

        if (
            locked_year.status
            == AcademicYear.Status.CLOSED
        ):
            raise AcademicYearClosingError(
                "Учебный год уже закрыт.",
                code="academic_year_already_closed",
            )

        readiness = (
            AcademicYearClosingReadinessService
            .ensure_ready(
                academic_year=locked_year,
                department_ids=None,
            )
        )

        if not readiness["ready_to_close"]:
            raise AcademicYearClosingError(
                (
                    "Учебный год не готов к закрытию. "
                    "Устраните блокирующие проблемы."
                ),
                code="academic_year_not_ready",
                details={
                    "readiness": readiness,
                },
            )

        old_values = cls._state_values(
            locked_year
        )

        closed_at = timezone.now()

        locked_year.status = (
            AcademicYear.Status.CLOSED
        )
        locked_year.closed_at = closed_at
        locked_year.closed_by = user
        locked_year.closing_comment = (
            comment.strip()
        )

        locked_year.is_current = False
        locked_year.is_active = False

        locked_year.reopened_at = None
        locked_year.reopened_by = None
        locked_year.reopening_reason = ""

        locked_year.updated_by = user

        locked_year.full_clean()
        locked_year.save(
            update_fields=(
                "status",
                "closed_at",
                "closed_by",
                "closing_comment",
                "is_current",
                "is_active",
                "reopened_at",
                "reopened_by",
                "reopening_reason",
                "updated_by",
                "updated_at",
            )
        )

        AuditService.log_status_change(
            instance=locked_year,
            old_status=old_values["status"],
            new_status=locked_year.status,
            actor=user,
            reason=locked_year.closing_comment,
            action=AuditEvent.Action.COMPLETE,
            action_label="Закрытие учебного года",
            metadata={
                "academic_year": locked_year.name,
                "old_values": old_values,
                "new_values": cls._state_values(
                    locked_year
                ),
                "readiness_summary": (
                    readiness["summary"]
                ),
                "warnings": readiness["warnings"],
            },
        )

        return locked_year, readiness

    @classmethod
    @transaction.atomic
    def reopen(
        cls,
        *,
        academic_year,
        user,
        reason,
    ):
        """
        Повторно открывает закрытый учебный год.
        """

        normalized_reason = (
            str(reason or "").strip()
        )

        if not normalized_reason:
            raise AcademicYearClosingError(
                (
                    "Для повторного открытия необходимо "
                    "указать причину."
                ),
                code="reopening_reason_required",
            )

        locked_year = (
            AcademicYear.objects
            .select_for_update()
            .get(pk=academic_year.pk)
        )

        if locked_year.is_archived:
            raise AcademicYearClosingError(
                (
                    "Архивный учебный год нельзя "
                    "повторно открыть."
                ),
                code="academic_year_archived",
            )

        if (
            locked_year.status
            != AcademicYear.Status.CLOSED
        ):
            raise AcademicYearClosingError(
                "Учебный год уже открыт.",
                code="academic_year_already_open",
            )

        old_values = cls._state_values(
            locked_year
        )

        locked_year.status = AcademicYear.Status.OPEN
        locked_year.closed_at = None
        locked_year.closed_by = None

        # Комментарий последнего закрытия сохраняется,
        # чтобы история была видна и вне журнала аудита.
        locked_year.reopened_at = timezone.now()
        locked_year.reopened_by = user
        locked_year.reopening_reason = (
            normalized_reason
        )

        locked_year.is_active = True

        # Год не становится текущим автоматически:
        # текущий год выбирается отдельной операцией.
        locked_year.is_current = False

        locked_year.updated_by = user

        locked_year.full_clean()
        locked_year.save(
            update_fields=(
                "status",
                "closed_at",
                "closed_by",
                "reopened_at",
                "reopened_by",
                "reopening_reason",
                "is_active",
                "is_current",
                "updated_by",
                "updated_at",
            )
        )

        AuditService.log_status_change(
            instance=locked_year,
            old_status=old_values["status"],
            new_status=locked_year.status,
            actor=user,
            reason=normalized_reason,
            action=AuditEvent.Action.RESTORE,
            action_label=(
                "Повторное открытие учебного года"
            ),
            metadata={
                "academic_year": locked_year.name,
                "old_values": old_values,
                "new_values": cls._state_values(
                    locked_year
                ),
            },
        )

        return locked_year

    @classmethod
    def ensure_open(
        cls,
        *,
        academic_year,
    ):
        """
        Универсальная проверка для сервисов,
        изменяющих данные учебного года.
        """

        if (
            academic_year.status
            == AcademicYear.Status.CLOSED
        ):
            raise AcademicYearClosingError(
                (
                    f"Учебный год {academic_year.name} "
                    "закрыт. Изменение данных запрещено."
                ),
                code="academic_year_closed",
                details={
                    "academic_year": academic_year.pk,
                    "academic_year_name": (
                        academic_year.name
                    ),
                    "closed_at": (
                        academic_year
                        .closed_at
                        .isoformat()
                        if academic_year.closed_at
                        else None
                    ),
                },
            )

        return academic_year

    @staticmethod
    def _state_values(
        academic_year,
    ) -> dict:
        return {
            "status": academic_year.status,
            "is_current": academic_year.is_current,
            "is_active": academic_year.is_active,
            "closed_at": (
                academic_year.closed_at.isoformat()
                if academic_year.closed_at
                else None
            ),
            "closed_by_id": (
                academic_year.closed_by_id
            ),
            "reopened_at": (
                academic_year.reopened_at.isoformat()
                if academic_year.reopened_at
                else None
            ),
            "reopened_by_id": (
                academic_year.reopened_by_id
            ),
        }