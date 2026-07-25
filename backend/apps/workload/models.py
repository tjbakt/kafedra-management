from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from apps.common.models import BaseModel
from apps.staff.models import StaffEmployment
from apps.teaching.models import PlannedWorkload


class WorkloadDistribution(BaseModel):
    """
    Распределение части плановой нагрузки преподавателю.

    Одна PlannedWorkload может быть разделена между несколькими
    трудовыми назначениями преподавателей.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", _("Черновик")
        APPROVED = "approved", _("Утверждено")
        CANCELLED = "cancelled", _("Отменено")

    planned_workload = models.ForeignKey(
        PlannedWorkload,
        verbose_name=_("Плановая нагрузка"),
        related_name="distributions",
        on_delete=models.PROTECT,
    )
    staff_employment = models.ForeignKey(
        StaffEmployment,
        verbose_name=_("Трудовое назначение преподавателя"),
        related_name="workload_distributions",
        on_delete=models.PROTECT,
    )
    allocated_hours = models.DecimalField(
        _("Распределённые часы"),
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
    )
    status = models.CharField(
        _("Статус"),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    approved_at = models.DateTimeField(
        _("Дата и время утверждения"),
        null=True,
        blank=True,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Утвердил"),
        related_name="approved_workload_distributions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    notes = models.TextField(
        _("Примечание"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Распределение нагрузки")
        verbose_name_plural = _("Распределение нагрузки")
        ordering = (
            "-planned_workload__academic_year__start_year",
            "planned_workload__teaching_department__name_ru",
            "staff_employment__staff_member__last_name",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "planned_workload",
                    "staff_employment",
                ),
                condition=Q(
                    is_archived=False,
                    status__in=("draft", "approved"),
                ),
                name="unique_active_workload_distribution",
            ),
            models.CheckConstraint(
                condition=Q(allocated_hours__gt=0),
                name="workload_distribution_hours_gt_zero",
            ),
        ]

    @property
    def staff_member(self):
        return self.staff_employment.staff_member

    @property
    def teacher_name(self) -> str:
        return self.staff_employment.staff_member.full_name

    @property
    def academic_year(self):
        return self.planned_workload.academic_year

    @property
    def teaching_department(self):
        return self.planned_workload.teaching_department

    def clean(self):
        super().clean()

        if not self.planned_workload_id or not self.staff_employment_id:
            return

        if self.allocated_hours <= 0:
            raise ValidationError(
                {
                    "allocated_hours": _(
                        "Количество распределённых часов "
                        "должно быть больше нуля."
                    )
                }
            )

        if self.staff_employment.is_archived:
            raise ValidationError(
                {
                    "staff_employment": _(
                        "Нельзя распределять нагрузку на архивное "
                        "трудовое назначение."
                    )
                }
            )

        if not self.staff_employment.is_active:
            raise ValidationError(
                {
                    "staff_employment": _(
                        "Трудовое назначение преподавателя неактивно."
                    )
                }
            )

        if not self.staff_employment.position.is_teaching_position:
            raise ValidationError(
                {
                    "staff_employment": _(
                        "Выбранная должность не участвует "
                        "в учебной нагрузке."
                    )
                }
            )

        if (
            self.staff_employment.department_id
            != self.planned_workload.teaching_department_id
        ):
            raise ValidationError(
                {
                    "staff_employment": _(
                        "Трудовое назначение преподавателя должно "
                        "относиться к кафедре плановой нагрузки."
                    )
                }
            )

        other_hours = (
            WorkloadDistribution.objects
            .filter(
                planned_workload=self.planned_workload,
                status__in=(
                    self.Status.DRAFT,
                    self.Status.APPROVED,
                ),
            )
            .exclude(pk=self.pk)
            .aggregate(
                total=models.Sum("allocated_hours")
            )["total"]
            or Decimal("0.00")
        )

        if other_hours + self.allocated_hours > (
            self.planned_workload.total_hours
        ):
            remaining = (
                self.planned_workload.total_hours
                - other_hours
            )

            raise ValidationError(
                {
                    "allocated_hours": _(
                        "Распределение превышает плановые часы. "
                        "Доступный остаток: %(remaining)s."
                    )
                    % {
                        "remaining": remaining,
                    }
                }
            )

    def __str__(self):
        return (
            f"{self.teacher_name}: "
            f"{self.allocated_hours} часов — "
            f"{self.planned_workload}"
        )