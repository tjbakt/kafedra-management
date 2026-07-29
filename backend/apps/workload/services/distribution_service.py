from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.audit.services.audit_service import AuditService
from apps.notifications.models import Notification
from apps.notifications.services.notification_service import (
    NotificationService,
)
from apps.staff.models import StaffEmploymentAcademicYear
from apps.teaching.models import PlannedWorkload
from apps.workload.models import WorkloadDistribution

from apps.academics.exceptions import (
    AcademicYearClosingError,
)
from apps.academics.services.academic_year_closing_service import (
    AcademicYearClosingService,
)


class WorkloadDistributionService:
    """
    Сервис создания, изменения, утверждения
    и отмены распределения учебной нагрузки.
    """

    ACTIVE_STATUSES = (
        WorkloadDistribution.Status.DRAFT,
        WorkloadDistribution.Status.APPROVED,
    )

    @classmethod
    def ensure_academic_year_open(
        cls,
        *,
        academic_year,
    ):
        """
        Запрещает изменение распределений закрытого
        учебного года.

        AcademicYearClosingService использует доменное
        исключение. WorkloadDistributionService
        преобразует его в стандартный ValidationError,
        который уже обрабатывается существующим API.
        """

        try:
            AcademicYearClosingService.ensure_open(
                academic_year=academic_year,
            )
        except AcademicYearClosingError as exc:
            details = exc.details or {}

            raise ValidationError(
                {
                    "code": exc.code,
                    "detail": exc.message,
                    "academic_year": (
                        details.get("academic_year")
                        or academic_year.pk
                    ),
                    "academic_year_name": (
                        details.get(
                            "academic_year_name"
                        )
                        or academic_year.name
                    ),
                    "closed_at": (
                        details.get("closed_at")
                        or (
                            academic_year
                            .closed_at
                            .isoformat()
                            if academic_year.closed_at
                            else None
                        )
                    ),
                }
            ) from exc

    @classmethod
    def get_available_actions(
        cls,
        *,
        distribution,
    ) -> dict:

        status = distribution.status

        academic_year = (
            distribution
            .planned_workload
            .academic_year
        )

        is_academic_year_closed = (
            academic_year.is_closed
        )

        closed_year_reason = (
            f"Учебный год {academic_year.name} закрыт. "
            "Изменение распределения запрещено."
        )

        is_draft = (
            status
            == WorkloadDistribution.Status.DRAFT
        )
        is_approved = (
            status
            == WorkloadDistribution.Status.APPROVED
        )
        is_cancelled = (
            status
            == WorkloadDistribution.Status.CANCELLED
        )

        result = {
            "distribution_id": distribution.pk,
            "status": status,
            "status_label": (
                distribution.get_status_display()
            ),
            "actions": {
                "approve": cls._action_availability(
                    allowed=is_draft,
                    unavailable_reason=(
                        cls._get_approve_unavailable_reason(
                            status=status
                        )
                    ),
                ),
                "return_to_draft": (
                    cls._action_availability(
                        allowed=is_approved,
                        unavailable_reason=(
                            cls
                            ._get_return_unavailable_reason(
                                status=status
                            )
                        ),
                    )
                ),
                "cancel": cls._action_availability(
                    allowed=not is_cancelled,
                    unavailable_reason=(
                        "Распределение уже отменено."
                        if is_cancelled
                        else ""
                    ),
                ),
                "restore": cls._action_availability(
                    allowed=is_cancelled,
                    unavailable_reason=(
                        cls
                        ._get_restore_unavailable_reason(
                            status=status
                        )
                    ),
                ),
                "transfer": cls._action_availability(
                    allowed=is_draft,
                    unavailable_reason=(
                        cls
                        ._get_transfer_unavailable_reason(
                            status=status
                        )
                    ),
                ),
                "edit": cls._action_availability(
                    allowed=is_draft,
                    unavailable_reason=(
                        cls._get_edit_unavailable_reason(
                            status=status
                        )
                    ),
                ),
            },
        }
        if is_academic_year_closed:
            for action in result["actions"].values():
                action["allowed"] = False
                action["reason"] = closed_year_reason

        return result

    @staticmethod
    def _action_availability(
        *,
        allowed,
        unavailable_reason="",
    ) -> dict:
        return {
            "allowed": allowed,
            "reason": (
                ""
                if allowed
                else unavailable_reason
            ),
        }

    @staticmethod
    def _get_approve_unavailable_reason(
        *,
        status,
    ) -> str:
        if (
            status
            == WorkloadDistribution.Status.APPROVED
        ):
            return "Распределение уже утверждено."

        if (
            status
            == WorkloadDistribution.Status.CANCELLED
        ):
            return (
                "Отменённое распределение нельзя "
                "утвердить. Сначала восстановите его."
            )

        return (
            "Распределение нельзя утвердить "
            "в текущем статусе."
        )

    @staticmethod
    def _get_return_unavailable_reason(
        *,
        status,
    ) -> str:
        if (
            status
            == WorkloadDistribution.Status.DRAFT
        ):
            return (
                "Распределение уже находится "
                "в статусе черновика."
            )

        if (
            status
            == WorkloadDistribution.Status.CANCELLED
        ):
            return (
                "Отменённое распределение нельзя "
                "вернуть из утверждения. "
                "Используйте восстановление."
            )

        return (
            "Вернуть в черновик можно только "
            "утверждённое распределение."
        )

    @staticmethod
    def _get_restore_unavailable_reason(
        *,
        status,
    ) -> str:
        if (
            status
            == WorkloadDistribution.Status.DRAFT
        ):
            return (
                "Черновое распределение уже активно "
                "и не требует восстановления."
            )

        if (
            status
            == WorkloadDistribution.Status.APPROVED
        ):
            return (
                "Утверждённое распределение уже "
                "активно и не требует восстановления."
            )

        return (
            "Восстановить можно только "
            "отменённое распределение."
        )

    @staticmethod
    def _get_transfer_unavailable_reason(
        *,
        status,
    ) -> str:
        if (
            status
            == WorkloadDistribution.Status.APPROVED
        ):
            return (
                "Нельзя переносить часы утверждённого "
                "распределения. Сначала верните его "
                "в черновик."
            )

        if (
            status
            == WorkloadDistribution.Status.CANCELLED
        ):
            return (
                "Нельзя переносить часы отменённого "
                "распределения. Сначала восстановите его."
            )

        return (
            "Перенос часов недоступен "
            "в текущем статусе."
        )

    @staticmethod
    def _get_edit_unavailable_reason(
        *,
        status,
    ) -> str:
        if (
            status
            == WorkloadDistribution.Status.APPROVED
        ):
            return (
                "Утверждённое распределение нельзя "
                "редактировать. Сначала верните его "
                "в черновик."
            )

        if (
            status
            == WorkloadDistribution.Status.CANCELLED
        ):
            return (
                "Отменённое распределение нельзя "
                "редактировать. Сначала восстановите его."
            )

        return (
            "Редактирование недоступно "
            "в текущем статусе."
        )

    @staticmethod
    def normalize_hours(value) -> Decimal:
        try:
            hours = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            raise ValidationError(
                {
                    "allocated_hours": (
                        "Количество часов должно быть числом."
                    )
                }
            )

        if hours <= Decimal("0.00"):
            raise ValidationError(
                {
                    "allocated_hours": (
                        "Количество часов должно быть больше нуля."
                    )
                }
            )

        return hours.quantize(Decimal("0.01"))

    @classmethod
    def get_distributed_hours(
        cls,
        planned_workload: PlannedWorkload,
        *,
        exclude_distribution=None,
    ) -> Decimal:
        queryset = WorkloadDistribution.objects.filter(
            planned_workload=planned_workload,
            status__in=cls.ACTIVE_STATUSES,
        )

        if exclude_distribution is not None:
            queryset = queryset.exclude(
                pk=exclude_distribution.pk
            )

        return (
            queryset.aggregate(
                total=Sum("allocated_hours")
            )["total"]
            or Decimal("0.00")
        )

    @classmethod
    def get_remaining_hours(
        cls,
        planned_workload: PlannedWorkload,
        *,
        exclude_distribution=None,
    ) -> Decimal:
        distributed = cls.get_distributed_hours(
            planned_workload,
            exclude_distribution=exclude_distribution,
        )

        return (
            planned_workload.total_hours - distributed
        ).quantize(Decimal("0.01"))

    @staticmethod
    def get_year_staff_record(
        *,
        planned_workload,
        staff_employment,
    ) -> StaffEmploymentAcademicYear:
        try:
            return (
                StaffEmploymentAcademicYear.objects
                .select_related(
                    "staff_employment",
                    "staff_employment__staff_member",
                    "staff_employment__department",
                    "academic_year",
                    "academic_degree",
                    "academic_title",
                )
                .get(
                    staff_employment=staff_employment,
                    academic_year=(
                        planned_workload.academic_year
                    ),
                    is_archived=False,
                    is_active=True,
                )
            )
        except StaffEmploymentAcademicYear.DoesNotExist:
            raise ValidationError(
                {
                    "staff_employment": (
                        "Для выбранного преподавателя отсутствуют "
                        "активные кадровые данные на учебный год "
                        f"«{planned_workload.academic_year}». "
                        "Сначала создайте годовую кадровую запись."
                    )
                }
            )

    @classmethod
    def validate_employment(
        cls,
        *,
        planned_workload,
        staff_employment,
    ) -> StaffEmploymentAcademicYear:
        if staff_employment.is_archived:
            raise ValidationError(
                {
                    "staff_employment": (
                        "Нельзя распределять нагрузку на "
                        "архивное трудовое назначение."
                    )
                }
            )

        if not staff_employment.is_active:
            raise ValidationError(
                {
                    "staff_employment": (
                        "Трудовое назначение преподавателя "
                        "неактивно."
                    )
                }
            )

        if not staff_employment.position.is_teaching_position:
            raise ValidationError(
                {
                    "staff_employment": (
                        "Выбранная должность не участвует "
                        "в учебной нагрузке."
                    )
                }
            )

        if (
            staff_employment.department_id
            != planned_workload.teaching_department_id
        ):
            raise ValidationError(
                {
                    "staff_employment": (
                        "Преподаватель должен относиться "
                        "к кафедре плановой нагрузки."
                    )
                }
            )

        return cls.get_year_staff_record(
            planned_workload=planned_workload,
            staff_employment=staff_employment,
        )

    @classmethod
    def validate_available_hours(
        cls,
        *,
        planned_workload,
        allocated_hours,
        exclude_distribution=None,
    ):
        remaining = cls.get_remaining_hours(
            planned_workload,
            exclude_distribution=exclude_distribution,
        )

        if allocated_hours > remaining:
            raise ValidationError(
                {
                    "allocated_hours": (
                        "Распределяемые часы превышают остаток. "
                        f"Доступно: {remaining}."
                    )
                }
            )

    @staticmethod
    def notify_teacher(
        *,
        distribution,
        title,
        message,
        notification_type,
        metadata=None,
    ):
        teacher_user = (
            distribution
            .staff_employment
            .staff_member
            .user
        )

        if not teacher_user:
            return

        NotificationService.notify(
            recipient=teacher_user,
            title=title,
            message=message,
            notification_type=notification_type,
            instance=distribution,
            action_url=(
                f"/workload/distributions/"
                f"{distribution.pk}"
            ),
            metadata=metadata or {},
        )

    @classmethod
    @transaction.atomic
    def create_distribution(
        cls,
        *,
        planned_workload,
        staff_employment,
        allocated_hours,
        user=None,
        notes="",
    ) -> WorkloadDistribution:
        planned_workload = (
            PlannedWorkload.objects
            .select_for_update()
            .select_related(
                "academic_year",
                "teaching_department",
            )
            .get(pk=planned_workload.pk)
        )
        cls.ensure_academic_year_open(
            academic_year=(
                planned_workload.academic_year
            ),
        )

        allocated_hours = cls.normalize_hours(
            allocated_hours
        )

        year_staff_record = cls.validate_employment(
            planned_workload=planned_workload,
            staff_employment=staff_employment,
        )

        cls.validate_available_hours(
            planned_workload=planned_workload,
            allocated_hours=allocated_hours,
        )

        distribution = WorkloadDistribution(
            planned_workload=planned_workload,
            staff_employment=staff_employment,
            allocated_hours=allocated_hours,
            status=WorkloadDistribution.Status.DRAFT,
            notes=notes,
            created_by=user,
            updated_by=user,
        )

        distribution.full_clean()
        distribution.save()

        cls.update_planned_workload_status(
            planned_workload=planned_workload,
            user=user,
        )

        AuditService.log(
            instance=distribution,
            action=AuditEvent.Action.DISTRIBUTE,
            actor=user,
            action_label=(
                "Нагрузка распределена преподавателю"
            ),
            new_values={
                "planned_workload": (
                    distribution.planned_workload_id
                ),
                "staff_employment": (
                    distribution.staff_employment_id
                ),
                "staff_employment_academic_year": (
                    year_staff_record.id
                ),
                "allocated_hours": (
                    distribution.allocated_hours
                ),
                "status": distribution.status,
            },
            changed_fields=[
                "planned_workload",
                "staff_employment",
                "allocated_hours",
                "status",
            ],
            reason=notes,
        )

        cls.notify_teacher(
            distribution=distribution,
            title="Назначена учебная нагрузка",
            message=(
                f"Вам назначено "
                f"{distribution.allocated_hours} часов: "
                f"{distribution.planned_workload}."
            ),
            notification_type=Notification.Type.INFO,
            metadata={
                "allocated_hours": str(
                    distribution.allocated_hours
                ),
                "academic_year_id": (
                    distribution
                    .planned_workload
                    .academic_year_id
                ),
                "year_staff_record_id": (
                    year_staff_record.id
                ),
            },
        )

        return distribution

    @classmethod
    @transaction.atomic
    def update_distribution(
        cls,
        *,
        distribution,
        allocated_hours,
        staff_employment=None,
        user=None,
        notes=None,
    ) -> WorkloadDistribution:
        distribution = (
            WorkloadDistribution.objects
            .select_for_update()
            .select_related(
                "planned_workload",
                "planned_workload__academic_year",
                "planned_workload__teaching_department",
                "staff_employment",
                "staff_employment__position",
            )
            .get(pk=distribution.pk)
        )
        cls.ensure_academic_year_open(
            academic_year=(
                distribution
                .planned_workload
                .academic_year
            ),
        )

        if (
            distribution.status
            == WorkloadDistribution.Status.APPROVED
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Утверждённое распределение нельзя "
                        "изменить. Сначала отмените утверждение."
                    )
                }
            )

        if (
            distribution.status
            == WorkloadDistribution.Status.CANCELLED
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Отменённое распределение нельзя изменить."
                    )
                }
            )

        allocated_hours = cls.normalize_hours(
            allocated_hours
        )

        selected_employment = (
            staff_employment
            or distribution.staff_employment
        )

        cls.validate_employment(
            planned_workload=distribution.planned_workload,
            staff_employment=selected_employment,
        )

        cls.validate_available_hours(
            planned_workload=distribution.planned_workload,
            allocated_hours=allocated_hours,
            exclude_distribution=distribution,
        )

        old_values = {
            "staff_employment": (
                distribution.staff_employment_id
            ),
            "allocated_hours": (
                distribution.allocated_hours
            ),
            "notes": distribution.notes,
        }

        distribution.staff_employment = (
            selected_employment
        )
        distribution.allocated_hours = (
            allocated_hours
        )

        if notes is not None:
            distribution.notes = notes

        distribution.updated_by = user
        distribution.full_clean()
        distribution.save()

        cls.update_planned_workload_status(
            planned_workload=distribution.planned_workload,
            user=user,
        )

        new_values = {
            "staff_employment": (
                distribution.staff_employment_id
            ),
            "allocated_hours": (
                distribution.allocated_hours
            ),
            "notes": distribution.notes,
        }

        AuditService.log(
            instance=distribution,
            action=AuditEvent.Action.UPDATE,
            actor=user,
            action_label=(
                "Изменено распределение нагрузки"
            ),
            old_values=old_values,
            new_values=new_values,
            changed_fields=[
                field_name
                for field_name in old_values
                if old_values[field_name]
                != new_values[field_name]
            ],
        )

        return distribution

    @classmethod
    @transaction.atomic
    def approve_distribution(
        cls,
        *,
        distribution,
        user,
    ) -> WorkloadDistribution:
        distribution = (
            WorkloadDistribution.objects
            .select_for_update()
            .select_related(
                "planned_workload",
                "planned_workload__academic_year",
                "planned_workload__teaching_department",
                "staff_employment",
                "staff_employment__position",
            )
            .get(pk=distribution.pk)
        )
        cls.ensure_academic_year_open(
            academic_year=(
                distribution
                .planned_workload
                .academic_year
            ),
        )

        if (
            distribution.status
            == WorkloadDistribution.Status.CANCELLED
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Отменённое распределение "
                        "нельзя утвердить."
                    )
                }
            )

        if (
            distribution.status
            == WorkloadDistribution.Status.APPROVED
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Распределение уже утверждено."
                    )
                }
            )

        cls.validate_employment(
            planned_workload=distribution.planned_workload,
            staff_employment=distribution.staff_employment,
        )

        cls.validate_available_hours(
            planned_workload=distribution.planned_workload,
            allocated_hours=(
                distribution.allocated_hours
            ),
            exclude_distribution=distribution,
        )

        old_status = distribution.status

        distribution.status = (
            WorkloadDistribution.Status.APPROVED
        )
        distribution.approved_at = timezone.now()
        distribution.approved_by = user
        distribution.updated_by = user

        distribution.full_clean()
        distribution.save(
            update_fields=(
                "status",
                "approved_at",
                "approved_by",
                "updated_by",
                "updated_at",
            )
        )

        cls.update_planned_workload_status(
            planned_workload=distribution.planned_workload,
            user=user,
        )

        AuditService.log_status_change(
            instance=distribution,
            old_status=old_status,
            new_status=distribution.status,
            actor=user,
            action=AuditEvent.Action.APPROVE,
            action_label=(
                "Распределение нагрузки утверждено"
            ),
            metadata={
                "approved_at": (
                    distribution.approved_at
                ),
                "approved_by": (
                    distribution.approved_by_id
                ),
                "allocated_hours": (
                    distribution.allocated_hours
                ),
            },
        )

        cls.notify_teacher(
            distribution=distribution,
            title="Учебная нагрузка утверждена",
            message=(
                "Распределение учебной нагрузки "
                f"на {distribution.allocated_hours} часов "
                "утверждено."
            ),
            notification_type=Notification.Type.SUCCESS,
        )

        return distribution

    @classmethod
    @transaction.atomic
    def return_distribution_to_draft(
            cls,
            *,
            distribution,
            user=None,
            reason="",
    ) -> WorkloadDistribution:
        """
        Возвращает утверждённое распределение
        в статус черновика.

        Количество распределённых часов не изменяется.
        """

        normalized_reason = str(reason or "").strip()

        if not normalized_reason:
            raise ValidationError(
                {
                    "reason": (
                        "Укажите причину возврата "
                        "распределения в черновик."
                    )
                }
            )

        distribution = (
            WorkloadDistribution.objects
            .select_for_update()
            .select_related(
                "planned_workload",
                "planned_workload__academic_year",
                "planned_workload__teaching_department",
                "staff_employment",
                "staff_employment__staff_member",
                "staff_employment__position",
                "approved_by",
            )
            .get(pk=distribution.pk)
        )
        cls.ensure_academic_year_open(
            academic_year=(
                distribution
                .planned_workload
                .academic_year
            ),
        )

        if (
                distribution.status
                != WorkloadDistribution.Status.APPROVED
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Вернуть в черновик можно только "
                        "утверждённое распределение."
                    )
                }
            )

        cls.validate_employment(
            planned_workload=distribution.planned_workload,
            staff_employment=distribution.staff_employment,
        )

        cls.validate_available_hours(
            planned_workload=distribution.planned_workload,
            allocated_hours=distribution.allocated_hours,
            exclude_distribution=distribution,
        )

        old_status = distribution.status
        old_approved_at = distribution.approved_at
        old_approved_by_id = distribution.approved_by_id

        distribution.status = (
            WorkloadDistribution.Status.DRAFT
        )
        distribution.approved_at = None
        distribution.approved_by = None
        distribution.updated_by = user

        distribution.notes = (
            f"{distribution.notes}\n"
            f"Причина возврата в черновик: "
            f"{normalized_reason}"
        ).strip()

        distribution.full_clean()
        distribution.save(
            update_fields=(
                "status",
                "approved_at",
                "approved_by",
                "notes",
                "updated_by",
                "updated_at",
            )
        )

        cls.update_planned_workload_status(
            planned_workload=distribution.planned_workload,
            user=user,
        )

        AuditService.log_status_change(
            instance=distribution,
            old_status=old_status,
            new_status=distribution.status,
            actor=user,
            action=AuditEvent.Action.RETURN,
            action_label=(
                "Утверждённое распределение "
                "возвращено в черновик"
            ),
            reason=normalized_reason,
            metadata={
                "allocated_hours": (
                    distribution.allocated_hours
                ),
                "old_approved_at": old_approved_at,
                "old_approved_by_id": (
                    old_approved_by_id
                ),
            },
        )

        cls.notify_teacher(
            distribution=distribution,
            title=(
                "Учебная нагрузка возвращена "
                "в черновик"
            ),
            message=(
                "Утверждение распределения "
                f"на {distribution.allocated_hours} часов "
                "отменено. Распределение возвращено "
                "в статус черновика. "
                f"Причина: {normalized_reason}"
            ),
            notification_type=Notification.Type.WARNING,
            metadata={
                "reason": normalized_reason,
                "status": WorkloadDistribution.Status.DRAFT,
                "allocated_hours": str(
                    distribution.allocated_hours
                ),
            },
        )

        return distribution

    @classmethod
    def return_distributions_to_draft(
            cls,
            *,
            distributions,
            user=None,
            reason="",
    ) -> dict:
        """
        Возвращает набор утверждённых распределений
        в черновик с частичным успехом.
        """

        normalized_reason = str(reason or "").strip()

        if not normalized_reason:
            raise ValidationError(
                {
                    "reason": (
                        "Укажите причину массового "
                        "возврата в черновик."
                    )
                }
            )

        returned_ids = []
        errors = []

        for distribution in distributions:
            try:
                returned = cls.return_distribution_to_draft(
                    distribution=distribution,
                    user=user,
                    reason=normalized_reason,
                )
            except ValidationError as exc:
                errors.append(
                    {
                        "id": distribution.pk,
                        "error": cls._validation_error_data(
                            exc
                        ),
                    }
                )
            else:
                returned_ids.append(returned.pk)

        return {
            "returned_count": len(returned_ids),
            "returned_ids": returned_ids,
            "errors_count": len(errors),
            "errors": errors,
        }

    @classmethod
    @transaction.atomic
    def cancel_distribution(
        cls,
        *,
        distribution,
        user=None,
        reason="",
    ) -> WorkloadDistribution:
        distribution = (
            WorkloadDistribution.objects
            .select_for_update()
            .select_related(
                "planned_workload",
                "planned_workload__academic_year",
                "planned_workload__teaching_department",
                "staff_employment",
                "staff_employment__staff_member",
            )
            .get(pk=distribution.pk)
        )
        cls.ensure_academic_year_open(
            academic_year=(
                distribution
                .planned_workload
                .academic_year
            ),
        )

        if (
            distribution.status
            == WorkloadDistribution.Status.CANCELLED
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Распределение уже отменено."
                    )
                }
            )

        old_status = distribution.status

        distribution.status = (
            WorkloadDistribution.Status.CANCELLED
        )
        distribution.approved_at = None
        distribution.approved_by = None
        distribution.updated_by = user

        if reason:
            distribution.notes = (
                f"{distribution.notes}\n"
                f"Причина отмены: {reason}"
            ).strip()

        distribution.save(
            update_fields=(
                "status",
                "approved_at",
                "approved_by",
                "notes",
                "updated_by",
                "updated_at",
            )
        )

        cls.update_planned_workload_status(
            planned_workload=distribution.planned_workload,
            user=user,
        )

        AuditService.log_status_change(
            instance=distribution,
            old_status=old_status,
            new_status=distribution.status,
            actor=user,
            action=AuditEvent.Action.CANCEL,
            action_label=(
                "Распределение нагрузки отменено"
            ),
            reason=reason,
            metadata={
                "allocated_hours": (
                    distribution.allocated_hours
                ),
            },
        )

        cls.notify_teacher(
            distribution=distribution,
            title="Распределение нагрузки отменено",
            message=(
                "Распределение на "
                f"{distribution.allocated_hours} часов "
                "отменено."
                + (
                    f" Причина: {reason}"
                    if reason
                    else ""
                )
            ),
            notification_type=Notification.Type.WARNING,
            metadata={
                "reason": reason,
            },
        )

        return distribution

    @classmethod
    @transaction.atomic
    def restore_distribution(
            cls,
            *,
            distribution,
            user=None,
            reason="",
    ) -> WorkloadDistribution:
        normalized_reason = str(reason or "").strip()

        if not normalized_reason:
            raise ValidationError(
                {
                    "reason": (
                        "Укажите причину восстановления "
                        "распределения."
                    )
                }
            )

        distribution = (
            WorkloadDistribution.objects
            .select_for_update()
            .select_related(
                "planned_workload",
                "planned_workload__academic_year",
                "planned_workload__teaching_department",
                "staff_employment",
                "staff_employment__staff_member",
                "staff_employment__position",
            )
            .get(pk=distribution.pk)
        )
        cls.ensure_academic_year_open(
            academic_year=(
                distribution
                .planned_workload
                .academic_year
            ),
        )

        if (
                distribution.status
                != WorkloadDistribution.Status.CANCELLED
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Восстановить можно только "
                        "отменённое распределение."
                    )
                }
            )

        cls.validate_employment(
            planned_workload=distribution.planned_workload,
            staff_employment=distribution.staff_employment,
        )

        cls.validate_available_hours(
            planned_workload=distribution.planned_workload,
            allocated_hours=distribution.allocated_hours,
        )

        old_status = distribution.status

        distribution.status = (
            WorkloadDistribution.Status.DRAFT
        )
        distribution.approved_at = None
        distribution.approved_by = None
        distribution.updated_by = user

        distribution.notes = (
            f"{distribution.notes}\n"
            f"Причина восстановления: {normalized_reason}"
        ).strip()

        distribution.full_clean()
        distribution.save(
            update_fields=(
                "status",
                "approved_at",
                "approved_by",
                "notes",
                "updated_by",
                "updated_at",
            )
        )

        cls.update_planned_workload_status(
            planned_workload=distribution.planned_workload,
            user=user,
        )

        AuditService.log_status_change(
            instance=distribution,
            old_status=old_status,
            new_status=distribution.status,
            actor=user,
            action=AuditEvent.Action.RESTORE,
            action_label=(
                "Распределение нагрузки восстановлено"
            ),
            reason=normalized_reason,
            metadata={
                "allocated_hours": (
                    distribution.allocated_hours
                ),
                "restored_as_status": (
                    WorkloadDistribution.Status.DRAFT
                ),
            },
        )

        cls.notify_teacher(
            distribution=distribution,
            title="Учебная нагрузка восстановлена",
            message=(
                "Ранее отменённое распределение "
                f"на {distribution.allocated_hours} часов "
                "восстановлено в статусе черновика. "
                f"Причина: {normalized_reason}"
            ),
            notification_type=Notification.Type.INFO,
            metadata={
                "reason": normalized_reason,
                "status": WorkloadDistribution.Status.DRAFT,
            },
        )

        return distribution

    @classmethod
    def cancel_distributions(
            cls,
            *,
            distributions,
            user=None,
            reason="",
    ) -> dict:
        """
        Отменяет набор распределений с частичным успехом.

        Ошибка одной записи не откатывает успешно отменённые
        записи. Метод возвращает подробный результат обработки.
        """

        normalized_reason = str(reason or "").strip()

        if not normalized_reason:
            raise ValidationError(
                {
                    "reason": (
                        "Укажите причину массовой отмены."
                    )
                }
            )

        cancelled_ids = []
        errors = []

        for distribution in distributions:
            try:
                cancelled = cls.cancel_distribution(
                    distribution=distribution,
                    user=user,
                    reason=normalized_reason,
                )
            except ValidationError as exc:
                errors.append(
                    {
                        "id": distribution.pk,
                        "error": cls._validation_error_data(
                            exc
                        ),
                    }
                )
            else:
                cancelled_ids.append(cancelled.pk)

        return {
            "cancelled_count": len(cancelled_ids),
            "cancelled_ids": cancelled_ids,
            "errors_count": len(errors),
            "errors": errors,
        }

    @classmethod
    def restore_distributions(
            cls,
            *,
            distributions,
            user=None,
            reason="",
    ) -> dict:
        normalized_reason = str(reason or "").strip()

        if not normalized_reason:
            raise ValidationError(
                {
                    "reason": (
                        "Укажите причину массового "
                        "восстановления."
                    )
                }
            )

        restored_ids = []
        errors = []

        for distribution in distributions:
            try:
                restored = cls.restore_distribution(
                    distribution=distribution,
                    user=user,
                    reason=normalized_reason,
                )
            except ValidationError as exc:
                errors.append(
                    {
                        "id": distribution.pk,
                        "error": (
                            cls._validation_error_data(
                                exc
                            )
                        ),
                    }
                )
            else:
                restored_ids.append(restored.pk)

        return {
            "restored_count": len(restored_ids),
            "restored_ids": restored_ids,
            "errors_count": len(errors),
            "errors": errors,
        }

    @classmethod
    @transaction.atomic
    def transfer_distribution_hours(
            cls,
            *,
            source_distribution,
            target_staff_employment,
            transfer_hours,
            user=None,
            reason="",
    ) -> dict:
        """
        Переносит часы чернового распределения
        другому преподавателю.

        Если у целевого преподавателя уже есть активный
        черновик для той же плановой нагрузки, часы
        добавляются к нему.

        При полном переносе исходное распределение
        переводится в статус CANCELLED.
        """

        normalized_reason = str(reason or "").strip()

        if not normalized_reason:
            raise ValidationError(
                {
                    "reason": (
                        "Укажите причину переноса часов."
                    )
                }
            )

        transfer_hours = cls.normalize_hours(
            transfer_hours
        )

        source_distribution = (
            WorkloadDistribution.objects
            .select_for_update()
            .select_related(
                "planned_workload",
                "planned_workload__academic_year",
                "planned_workload__teaching_department",
                "staff_employment",
                "staff_employment__staff_member",
                "staff_employment__position",
            )
            .get(pk=source_distribution.pk)
        )

        planned_workload = (
            PlannedWorkload.objects
            .select_for_update()
            .select_related(
                "academic_year",
                "teaching_department",
            )
            .get(
                pk=source_distribution.planned_workload_id
            )
        )
        cls.ensure_academic_year_open(
            academic_year=(
                planned_workload.academic_year
            ),
        )

        if (
                source_distribution.status
                != WorkloadDistribution.Status.DRAFT
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Переносить часы можно только "
                        "из чернового распределения."
                    )
                }
            )

        if (
                source_distribution.staff_employment_id
                == target_staff_employment.pk
        ):
            raise ValidationError(
                {
                    "target_staff_employment": (
                        "Исходный и целевой преподаватель "
                        "не должны совпадать."
                    )
                }
            )

        if (
                transfer_hours
                > source_distribution.allocated_hours
        ):
            raise ValidationError(
                {
                    "transfer_hours": (
                        "Количество переносимых часов "
                        "превышает часы исходного "
                        "распределения. "
                        f"Доступно: "
                        f"{source_distribution.allocated_hours}."
                    )
                }
            )

        year_staff_record = cls.validate_employment(
            planned_workload=planned_workload,
            staff_employment=target_staff_employment,
        )

        target_distribution = (
            WorkloadDistribution.objects
            .select_for_update()
            .select_related(
                "staff_employment",
                "staff_employment__staff_member",
                "staff_employment__position",
            )
            .filter(
                planned_workload=planned_workload,
                staff_employment=target_staff_employment,
                status__in=cls.ACTIVE_STATUSES,
                is_archived=False,
            )
            .first()
        )

        if (
                target_distribution is not None
                and target_distribution.status
                == WorkloadDistribution.Status.APPROVED
        ):
            raise ValidationError(
                {
                    "target_staff_employment": (
                        "У целевого преподавателя уже есть "
                        "утверждённое распределение по этой "
                        "плановой нагрузке. Сначала отмените "
                        "его утверждение."
                    )
                }
            )

        source_old_hours = (
            source_distribution.allocated_hours
        )
        source_remaining_hours = (
                source_old_hours - transfer_hours
        ).quantize(Decimal("0.01"))

        source_old_status = source_distribution.status

        if source_remaining_hours == Decimal("0.00"):
            source_distribution.status = (
                WorkloadDistribution.Status.CANCELLED
            )
            source_distribution.approved_at = None
            source_distribution.approved_by = None
        else:
            source_distribution.allocated_hours = (
                source_remaining_hours
            )

        source_distribution.notes = (
            f"{source_distribution.notes}\n"
            f"Перенесено {transfer_hours} часов "
            f"на трудовое назначение "
            f"ID {target_staff_employment.pk}. "
            f"Причина: {normalized_reason}"
        ).strip()
        source_distribution.updated_by = user

        if source_remaining_hours == Decimal("0.00"):
            source_distribution.save(
                update_fields=(
                    "status",
                    "approved_at",
                    "approved_by",
                    "notes",
                    "updated_by",
                    "updated_at",
                )
            )
        else:
            source_distribution.full_clean()
            source_distribution.save(
                update_fields=(
                    "allocated_hours",
                    "notes",
                    "updated_by",
                    "updated_at",
                )
            )

        target_created = target_distribution is None

        if target_created:
            target_distribution = WorkloadDistribution(
                planned_workload=planned_workload,
                staff_employment=target_staff_employment,
                allocated_hours=transfer_hours,
                status=WorkloadDistribution.Status.DRAFT,
                notes=(
                    f"Получено {transfer_hours} часов "
                    f"из распределения "
                    f"ID {source_distribution.pk}. "
                    f"Причина: {normalized_reason}"
                ),
                created_by=user,
                updated_by=user,
            )
        else:
            target_old_hours = (
                target_distribution.allocated_hours
            )
            target_distribution.allocated_hours = (
                    target_old_hours + transfer_hours
            ).quantize(Decimal("0.01"))
            target_distribution.notes = (
                f"{target_distribution.notes}\n"
                f"Добавлено {transfer_hours} часов "
                f"из распределения "
                f"ID {source_distribution.pk}. "
                f"Причина: {normalized_reason}"
            ).strip()
            target_distribution.updated_by = user

        target_distribution.full_clean()

        if target_created:
            target_distribution.save()
        else:
            target_distribution.save(
                update_fields=(
                    "allocated_hours",
                    "notes",
                    "updated_by",
                    "updated_at",
                )
            )

        cls.update_planned_workload_status(
            planned_workload=planned_workload,
            user=user,
        )

        AuditService.log(
            instance=source_distribution,
            action=AuditEvent.Action.UPDATE,
            actor=user,
            action_label=(
                "Часы нагрузки перенесены "
                "другому преподавателю"
            ),
            old_values={
                "allocated_hours": source_old_hours,
                "status": source_old_status,
            },
            new_values={
                "allocated_hours": (
                    source_remaining_hours
                    if source_remaining_hours
                       > Decimal("0.00")
                    else Decimal("0.00")
                ),
                "status": source_distribution.status,
            },
            changed_fields=[
                "allocated_hours",
                "status",
            ],
            reason=normalized_reason,
            metadata={
                "operation": "transfer_hours",
                "target_distribution_id": (
                    target_distribution.pk
                ),
                "target_staff_employment_id": (
                    target_staff_employment.pk
                ),
                "target_year_staff_record_id": (
                    year_staff_record.pk
                ),
                "transferred_hours": transfer_hours,
            },
        )

        AuditService.log(
            instance=target_distribution,
            action=(
                AuditEvent.Action.DISTRIBUTE
                if target_created
                else AuditEvent.Action.UPDATE
            ),
            actor=user,
            action_label=(
                "Получены часы нагрузки "
                "от другого преподавателя"
            ),
            old_values=(
                {}
                if target_created
                else {
                    "allocated_hours": (
                            target_distribution.allocated_hours
                            - transfer_hours
                    )
                }
            ),
            new_values={
                "allocated_hours": (
                    target_distribution.allocated_hours
                ),
                "status": target_distribution.status,
            },
            changed_fields=[
                "allocated_hours",
                "status",
            ],
            reason=normalized_reason,
            metadata={
                "operation": "receive_transferred_hours",
                "source_distribution_id": (
                    source_distribution.pk
                ),
                "source_staff_employment_id": (
                    source_distribution
                    .staff_employment_id
                ),
                "transferred_hours": transfer_hours,
            },
        )

        cls.notify_teacher(
            distribution=source_distribution,
            title="Часть учебной нагрузки перенесена",
            message=(
                f"Из вашего распределения перенесено "
                f"{transfer_hours} часов. "
                f"Причина: {normalized_reason}"
            ),
            notification_type=(
                Notification.Type.WARNING
            ),
            metadata={
                "operation": "transfer_hours",
                "transferred_hours": str(
                    transfer_hours
                ),
                "target_distribution_id": (
                    target_distribution.pk
                ),
            },
        )

        cls.notify_teacher(
            distribution=target_distribution,
            title="Добавлена учебная нагрузка",
            message=(
                f"Вам передано {transfer_hours} часов "
                "учебной нагрузки. "
                f"Причина: {normalized_reason}"
            ),
            notification_type=(
                Notification.Type.INFO
            ),
            metadata={
                "operation": (
                    "receive_transferred_hours"
                ),
                "transferred_hours": str(
                    transfer_hours
                ),
                "source_distribution_id": (
                    source_distribution.pk
                ),
            },
        )

        return {
            "source_distribution": (
                source_distribution
            ),
            "target_distribution": (
                target_distribution
            ),
            "transferred_hours": transfer_hours,
            "source_cancelled": (
                    source_distribution.status
                    == WorkloadDistribution.Status.CANCELLED
            ),
            "target_created": target_created,
        }

    @staticmethod
    def _validation_error_data(exc):
        """
        Преобразует django.core.exceptions.ValidationError
        в JSON-совместимую структуру.
        """

        if hasattr(exc, "message_dict"):
            return exc.message_dict

        if hasattr(exc, "messages"):
            return exc.messages

        return [str(exc)]

    @classmethod
    def update_planned_workload_status(
        cls,
        *,
        planned_workload,
        user=None,
    ):
        distributed = cls.get_distributed_hours(
            planned_workload
        )

        remaining = (
            planned_workload.total_hours - distributed
        )

        if distributed <= Decimal("0.00"):
            status = PlannedWorkload.Status.CALCULATED
        elif remaining > Decimal("0.00"):
            status = (
                PlannedWorkload.Status.PARTIALLY_DISTRIBUTED
            )
        else:
            status = PlannedWorkload.Status.DISTRIBUTED

        if planned_workload.status == status:
            return

        planned_workload.status = status
        planned_workload.updated_by = user
        planned_workload.save(
            update_fields=(
                "status",
                "updated_by",
                "updated_at",
            )
        )