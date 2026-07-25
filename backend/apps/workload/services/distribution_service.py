from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.teaching.models import PlannedWorkload
from apps.workload.models import WorkloadDistribution

from apps.audit.models import AuditEvent
from apps.audit.services.audit_service import AuditService

from apps.notifications.models import Notification
from apps.notifications.services.notification_service import (
    NotificationService,
)


class WorkloadDistributionService:
    """
    Сервис создания, изменения и утверждения распределения.
    """

    @staticmethod
    def get_distributed_hours(
        planned_workload: PlannedWorkload,
        *,
        exclude_distribution=None,
    ) -> Decimal:
        queryset = WorkloadDistribution.objects.filter(
            planned_workload=planned_workload,
            status__in=(
                WorkloadDistribution.Status.DRAFT,
                WorkloadDistribution.Status.APPROVED,
            ),
        )

        if exclude_distribution:
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

        return planned_workload.total_hours - distributed

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
            .get(pk=planned_workload.pk)
        )

        allocated_hours = Decimal(allocated_hours)

        remaining = cls.get_remaining_hours(
            planned_workload
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
            action_label="Нагрузка распределена преподавателю",
            new_values={
                "planned_workload": distribution.planned_workload_id,
                "staff_employment": distribution.staff_employment_id,
                "allocated_hours": distribution.allocated_hours,
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

        teacher_user = (
            distribution
            .staff_employment
            .staff_member
            .user
        )

        if teacher_user:
            NotificationService.notify(
                recipient=teacher_user,
                title="Назначена учебная нагрузка",
                message=(
                    f"Вам назначено "
                    f"{distribution.allocated_hours} часов: "
                    f"{distribution.planned_workload}."
                ),
                notification_type=Notification.Type.INFO,
                instance=distribution,
                action_url=(
                    f"/workload/distributions/"
                    f"{distribution.pk}"
                ),
                metadata={
                    "allocated_hours": str(
                        distribution.allocated_hours
                    ),
                    "academic_year_id": (
                        distribution
                        .planned_workload
                        .academic_year_id
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
        user=None,
        notes=None,
    ) -> WorkloadDistribution:
        distribution = (
            WorkloadDistribution.objects
            .select_for_update()
            .select_related("planned_workload")
            .get(pk=distribution.pk)
        )

        if (
            distribution.status
            == WorkloadDistribution.Status.APPROVED
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Утверждённое распределение нельзя изменить. "
                        "Сначала отмените утверждение."
                    )
                }
            )

        allocated_hours = Decimal(allocated_hours)

        remaining = cls.get_remaining_hours(
            distribution.planned_workload,
            exclude_distribution=distribution,
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

        distribution.allocated_hours = allocated_hours

        if notes is not None:
            distribution.notes = notes

        distribution.updated_by = user

        old_values = {
            "allocated_hours": distribution.allocated_hours,
            "notes": distribution.notes,
        }

        distribution.full_clean()
        distribution.save()

        cls.update_planned_workload_status(
            planned_workload=distribution.planned_workload,
            user=user,
        )

        AuditService.log(
            instance=distribution,
            action=AuditEvent.Action.UPDATE,
            actor=user,
            action_label="Изменено распределение нагрузки",
            old_values=old_values,
            new_values={
                "allocated_hours": distribution.allocated_hours,
                "notes": distribution.notes,
            },
            changed_fields=[
                field_name
                for field_name in (
                    "allocated_hours",
                    "notes",
                )
                if old_values[field_name]
                   != getattr(distribution, field_name)
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
            .select_related("planned_workload")
            .get(pk=distribution.pk)
        )

        if (
            distribution.status
            == WorkloadDistribution.Status.CANCELLED
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Отменённое распределение нельзя утвердить."
                    )
                }
            )

        distribution.status = (
            WorkloadDistribution.Status.APPROVED
        )
        distribution.approved_at = timezone.now()
        distribution.approved_by = user
        distribution.updated_by = user

        old_status = distribution.status

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
            action_label="Распределение нагрузки утверждено",
            metadata={
                "approved_at": distribution.approved_at,
                "approved_by": distribution.approved_by_id,
                "allocated_hours": distribution.allocated_hours,
            },
        )

        teacher_user = (
            distribution
            .staff_employment
            .staff_member
            .user
        )

        if teacher_user:
            NotificationService.notify(
                recipient=teacher_user,
                title="Учебная нагрузка утверждена",
                message=(
                    f"Распределение учебной нагрузки "
                    f"на {distribution.allocated_hours} часов "
                    f"утверждено."
                ),
                notification_type=Notification.Type.SUCCESS,
                instance=distribution,
                action_url=(
                    f"/workload/distributions/"
                    f"{distribution.pk}"
                ),
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
            .select_related("planned_workload")
            .get(pk=distribution.pk)
        )

        distribution.status = (
            WorkloadDistribution.Status.CANCELLED
        )
        distribution.approved_at = None
        distribution.approved_by = None
        distribution.updated_by = user

        old_status = distribution.status

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
            action=AuditEvent.Action.CANCEL,
            action_label="Распределение нагрузки отменено",
            reason=reason,
            metadata={
                "allocated_hours": distribution.allocated_hours,
            },
        )

        teacher_user = (
            distribution
            .staff_employment
            .staff_member
            .user
        )

        if teacher_user:
            NotificationService.notify(
                recipient=teacher_user,
                title="Распределение нагрузки отменено",
                message=(
                    f"Распределение на "
                    f"{distribution.allocated_hours} часов отменено. "
                    f"Причина: {reason}"
                ),
                notification_type=Notification.Type.WARNING,
                instance=distribution,
                action_url=(
                    f"/workload/distributions/"
                    f"{distribution.pk}"
                ),
                metadata={
                    "reason": reason,
                },
            )

        return distribution

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

        planned_workload.status = status
        planned_workload.updated_by = user
        planned_workload.save(
            update_fields=(
                "status",
                "updated_by",
                "updated_at",
            )
        )