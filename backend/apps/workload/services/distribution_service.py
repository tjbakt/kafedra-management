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


class WorkloadDistributionService:
    """
    Сервис создания, изменения, утверждения
    и отмены распределения учебной нагрузки.
    """

    ACTIVE_STATUSES = (
        WorkloadDistribution.Status.DRAFT,
        WorkloadDistribution.Status.APPROVED,
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
                "staff_employment",
                "staff_employment__staff_member",
            )
            .get(pk=distribution.pk)
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