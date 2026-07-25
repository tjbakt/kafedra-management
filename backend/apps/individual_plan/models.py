from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.academics.models import AcademicSemester, AcademicYear
from apps.common.models import BaseModel
from apps.staff.models import StaffEmployment
from apps.workload.models import WorkloadDistribution


class IndividualPlanSection(BaseModel):
    """
    Раздел индивидуального плана преподавателя.
    """

    class Code(models.TextChoices):
        TEACHING = "teaching", _("Учебная работа")
        METHODOLOGICAL = (
            "methodological",
            _("Учебно-методическая работа"),
        )
        SCIENTIFIC = "scientific", _("Научная работа")
        ORGANIZATIONAL = (
            "organizational",
            _("Организационная работа"),
        )
        EDUCATIONAL = (
            "educational",
            _("Воспитательная работа"),
        )
        PROFESSIONAL_DEVELOPMENT = (
            "professional_development",
            _("Повышение квалификации"),
        )
        OTHER = "other", _("Другие виды работы")

    code = models.CharField(
        _("Код"),
        max_length=40,
        choices=Code.choices,
        unique=True,
    )
    name_ru = models.CharField(
        _("Название на русском"),
        max_length=255,
    )
    name_uz = models.CharField(
        _("Название на узбекском"),
        max_length=255,
    )
    is_hourly = models.BooleanField(
        _("Учитывать часы"),
        default=True,
    )
    is_active = models.BooleanField(
        _("Активен"),
        default=True,
        db_index=True,
    )
    sort_order = models.PositiveIntegerField(
        _("Порядок сортировки"),
        default=0,
    )

    class Meta:
        verbose_name = _("Раздел индивидуального плана")
        verbose_name_plural = _("Разделы индивидуального плана")
        ordering = ("sort_order", "name_ru")

    def __str__(self):
        return self.name_ru

class IndividualActivityType(BaseModel):
    """
    Вид деятельности внутри раздела индивидуального плана.

    Примеры:
    - подготовка учебного пособия;
    - публикация статьи;
    - участие в конференции;
    - кураторская работа;
    - разработка методических указаний.
    """

    section = models.ForeignKey(
        IndividualPlanSection,
        verbose_name=_("Раздел"),
        related_name="activity_types",
        on_delete=models.PROTECT,
    )
    code = models.CharField(
        _("Код"),
        max_length=80,
        unique=True,
        db_index=True,
    )
    name_ru = models.CharField(
        _("Название на русском"),
        max_length=500,
    )
    name_uz = models.CharField(
        _("Название на узбекском"),
        max_length=500,
    )
    default_hours = models.DecimalField(
        _("Рекомендуемые часы"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )
    requires_evidence = models.BooleanField(
        _("Требуется подтверждение"),
        default=False,
    )
    is_active = models.BooleanField(
        _("Активен"),
        default=True,
        db_index=True,
    )
    sort_order = models.PositiveIntegerField(
        _("Порядок сортировки"),
        default=0,
    )

    class Meta:
        verbose_name = _("Вид работы индивидуального плана")
        verbose_name_plural = _("Виды работ индивидуального плана")
        ordering = (
            "section__sort_order",
            "sort_order",
            "name_ru",
        )

    def __str__(self):
        return f"{self.section}: {self.name_ru}"

class IndividualPlan(BaseModel):
    """
    Годовой индивидуальный план по одному трудовому назначению.

    Если преподаватель работает на нескольких кафедрах,
    для каждого назначения может быть отдельный план.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", _("Черновик")
        SUBMITTED = "submitted", _("Отправлен на рассмотрение")
        RETURNED = "returned", _("Возвращён на доработку")
        APPROVED = "approved", _("Утверждён")
        IN_PROGRESS = "in_progress", _("Выполняется")
        COMPLETED = "completed", _("Завершён")
        CLOSED = "closed", _("Закрыт")

    staff_employment = models.ForeignKey(
        StaffEmployment,
        verbose_name=_("Трудовое назначение"),
        related_name="individual_plans",
        on_delete=models.PROTECT,
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        verbose_name=_("Учебный год"),
        related_name="individual_plans",
        on_delete=models.PROTECT,
    )
    status = models.CharField(
        _("Статус"),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    submitted_at = models.DateTimeField(
        _("Дата отправки"),
        null=True,
        blank=True,
    )
    approved_at = models.DateTimeField(
        _("Дата утверждения"),
        null=True,
        blank=True,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Утвердил"),
        related_name="approved_individual_plans",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    closed_at = models.DateTimeField(
        _("Дата закрытия"),
        null=True,
        blank=True,
    )
    teacher_notes = models.TextField(
        _("Примечание преподавателя"),
        blank=True,
    )
    reviewer_notes = models.TextField(
        _("Комментарий проверяющего"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Индивидуальный план")
        verbose_name_plural = _("Индивидуальные планы")
        ordering = (
            "-academic_year__start_year",
            "staff_employment__staff_member__last_name",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "staff_employment",
                    "academic_year",
                ),
                condition=Q(is_archived=False),
                name="unique_employment_individual_plan_year",
            ),
        ]

    @property
    def staff_member(self):
        return self.staff_employment.staff_member

    @property
    def teacher_name(self):
        return self.staff_employment.staff_member.full_name

    @property
    def department(self):
        return self.staff_employment.department

    @property
    def planned_hours(self):
        return (
            self.items.filter(
                is_archived=False,
                status__in=(
                    IndividualPlanItem.Status.PLANNED,
                    IndividualPlanItem.Status.IN_PROGRESS,
                    IndividualPlanItem.Status.COMPLETED,
                    IndividualPlanItem.Status.CONFIRMED,
                ),
            ).aggregate(
                total=Sum("planned_hours")
            )["total"]
            or Decimal("0.00")
        )

    @property
    def actual_hours(self):
        return (
            self.items.filter(
                is_archived=False,
                status__in=(
                    IndividualPlanItem.Status.COMPLETED,
                    IndividualPlanItem.Status.CONFIRMED,
                ),
            ).aggregate(
                total=Sum("actual_hours")
            )["total"]
            or Decimal("0.00")
        )

    @property
    def completion_percent(self):
        if self.planned_hours <= 0:
            return Decimal("0.00")

        return (
            self.actual_hours
            / self.planned_hours
            * Decimal("100.00")
        ).quantize(Decimal("0.01"))

    def clean(self):
        super().clean()

        if not self.staff_employment_id:
            return

        if self.staff_employment.is_archived:
            raise ValidationError(
                {
                    "staff_employment": _(
                        "Нельзя создать план для архивного назначения."
                    )
                }
            )

        if not self.staff_employment.is_active:
            raise ValidationError(
                {
                    "staff_employment": _(
                        "Трудовое назначение неактивно."
                    )
                }
            )

        if not self.staff_employment.position.is_teaching_position:
            raise ValidationError(
                {
                    "staff_employment": _(
                        "Индивидуальный план доступен только "
                        "для преподавательских должностей."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.teacher_name} — "
            f"{self.academic_year}"
        )

class IndividualPlanItem(BaseModel):
    """
    Отдельный пункт индивидуального плана.
    """

    class Status(models.TextChoices):
        PLANNED = "planned", _("Запланирован")
        IN_PROGRESS = "in_progress", _("Выполняется")
        COMPLETED = "completed", _("Выполнен")
        CONFIRMED = "confirmed", _("Подтверждён")
        REJECTED = "rejected", _("Не подтверждён")
        CANCELLED = "cancelled", _("Отменён")

    individual_plan = models.ForeignKey(
        IndividualPlan,
        verbose_name=_("Индивидуальный план"),
        related_name="items",
        on_delete=models.CASCADE,
    )
    section = models.ForeignKey(
        IndividualPlanSection,
        verbose_name=_("Раздел"),
        related_name="plan_items",
        on_delete=models.PROTECT,
    )
    activity_type = models.ForeignKey(
        IndividualActivityType,
        verbose_name=_("Вид работы"),
        related_name="plan_items",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    academic_semester = models.ForeignKey(
        AcademicSemester,
        verbose_name=_("Семестр выполнения"),
        related_name="individual_plan_items",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    title = models.CharField(
        _("Наименование работы"),
        max_length=1000,
    )
    description = models.TextField(
        _("Описание"),
        blank=True,
    )
    planned_hours = models.DecimalField(
        _("Плановые часы"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )
    actual_hours = models.DecimalField(
        _("Фактические часы"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )
    planned_start_date = models.DateField(
        _("Плановая дата начала"),
        null=True,
        blank=True,
    )
    planned_end_date = models.DateField(
        _("Плановая дата окончания"),
        null=True,
        blank=True,
    )
    actual_completion_date = models.DateField(
        _("Дата фактического выполнения"),
        null=True,
        blank=True,
    )
    expected_result = models.TextField(
        _("Ожидаемый результат"),
        blank=True,
    )
    actual_result = models.TextField(
        _("Фактический результат"),
        blank=True,
    )
    evidence_url = models.URLField(
        _("Ссылка на подтверждение"),
        blank=True,
    )
    evidence_document = models.CharField(
        _("Реквизиты подтверждающего документа"),
        max_length=500,
        blank=True,
    )
    status = models.CharField(
        _("Статус"),
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
        db_index=True,
    )
    confirmed_at = models.DateTimeField(
        _("Дата подтверждения"),
        null=True,
        blank=True,
    )
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Подтвердил"),
        related_name="confirmed_individual_plan_items",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    teacher_comment = models.TextField(
        _("Комментарий преподавателя"),
        blank=True,
    )
    reviewer_comment = models.TextField(
        _("Комментарий проверяющего"),
        blank=True,
    )
    sort_order = models.PositiveIntegerField(
        _("Порядок"),
        default=0,
    )

    class Meta:
        verbose_name = _("Пункт индивидуального плана")
        verbose_name_plural = _("Пункты индивидуального плана")
        ordering = (
            "section__sort_order",
            "sort_order",
            "planned_end_date",
            "title",
        )

    def clean(self):
        super().clean()

        if (
            self.activity_type_id
            and self.section_id
            and self.activity_type.section_id != self.section_id
        ):
            raise ValidationError(
                {
                    "activity_type": _(
                        "Выбранный вид работы не относится "
                        "к указанному разделу."
                    )
                }
            )

        if (
            self.academic_semester_id
            and self.individual_plan_id
            and self.academic_semester.academic_year_id
            != self.individual_plan.academic_year_id
        ):
            raise ValidationError(
                {
                    "academic_semester": _(
                        "Семестр должен относиться к учебному году "
                        "индивидуального плана."
                    )
                }
            )

        if (
            self.planned_start_date
            and self.planned_end_date
            and self.planned_end_date < self.planned_start_date
        ):
            raise ValidationError(
                {
                    "planned_end_date": _(
                        "Дата окончания не может быть раньше "
                        "даты начала."
                    )
                }
            )

        if (
            self.status
            in (
                self.Status.COMPLETED,
                self.Status.CONFIRMED,
            )
            and not self.actual_completion_date
        ):
            raise ValidationError(
                {
                    "actual_completion_date": _(
                        "Для выполненного пункта необходимо "
                        "указать дату выполнения."
                    )
                }
            )

        if (
            self.status == self.Status.CONFIRMED
            and not self.confirmed_by_id
        ):
            raise ValidationError(
                {
                    "confirmed_by": _(
                        "Для подтверждённого пункта необходимо "
                        "указать проверяющего."
                    )
                }
            )

        requires_evidence = (
            self.activity_type_id
            and self.activity_type.requires_evidence
        )

        if (
            requires_evidence
            and self.status
            in (
                self.Status.COMPLETED,
                self.Status.CONFIRMED,
            )
            and not self.evidence_url
            and not self.evidence_document
        ):
            raise ValidationError(
                {
                    "evidence_document": _(
                        "Для этого вида работы требуется "
                        "подтверждающий документ или ссылка."
                    )
                }
            )

    def __str__(self):
        return self.title

class IndividualPlanTeachingWorkload(BaseModel):
    """
    Связь пункта индивидуального плана с распределённой
    учебной нагрузкой преподавателя.
    """

    plan_item = models.OneToOneField(
        IndividualPlanItem,
        verbose_name=_("Пункт индивидуального плана"),
        related_name="teaching_workload_link",
        on_delete=models.CASCADE,
    )
    workload_distribution = models.OneToOneField(
        WorkloadDistribution,
        verbose_name=_("Распределение учебной нагрузки"),
        related_name="individual_plan_link",
        on_delete=models.PROTECT,
    )
    imported_hours = models.DecimalField(
        _("Импортированные часы"),
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )

    class Meta:
        verbose_name = _("Учебная нагрузка индивидуального плана")
        verbose_name_plural = _(
            "Учебная нагрузка индивидуальных планов"
        )

    def clean(self):
        super().clean()

        if not self.plan_item_id or not self.workload_distribution_id:
            return

        distribution = self.workload_distribution
        plan = self.plan_item.individual_plan

        if (
            distribution.staff_employment_id
            != plan.staff_employment_id
        ):
            raise ValidationError(
                {
                    "workload_distribution": _(
                        "Распределение относится к другому "
                        "трудовому назначению."
                    )
                }
            )

        if (
            distribution.planned_workload.academic_year_id
            != plan.academic_year_id
        ):
            raise ValidationError(
                {
                    "workload_distribution": _(
                        "Распределение относится к другому "
                        "учебному году."
                    )
                }
            )

        if (
            distribution.status
            != WorkloadDistribution.Status.APPROVED
        ):
            raise ValidationError(
                {
                    "workload_distribution": _(
                        "В индивидуальный план можно импортировать "
                        "только утверждённую нагрузку."
                    )
                }
            )

    def __str__(self):
        return str(self.workload_distribution)