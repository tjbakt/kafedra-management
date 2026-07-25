from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.academics.models import AcademicYear
from apps.common.models import BaseModel
from apps.organizations.models import Department


class StaffPosition(BaseModel):
    """
    Должность преподавателя или сотрудника.
    """

    class Category(models.TextChoices):
        TEACHING = "teaching", _("Профессорско-преподавательский состав")
        ADMINISTRATIVE = "administrative", _("Административный персонал")
        SUPPORT = "support", _("Учебно-вспомогательный персонал")
        OTHER = "other", _("Другой персонал")

    code = models.CharField(
        _("Код"),
        max_length=50,
        unique=True,
        db_index=True,
    )
    name_ru = models.CharField(
        _("Название на русском"),
        max_length=255,
    )
    name_uz = models.CharField(
        _("Название на узбекском"),
        max_length=255,
    )
    category = models.CharField(
        _("Категория"),
        max_length=20,
        choices=Category.choices,
        default=Category.TEACHING,
        db_index=True,
    )
    is_teaching_position = models.BooleanField(
        _("Участвует в учебной нагрузке"),
        default=True,
        db_index=True,
    )
    is_active = models.BooleanField(
        _("Активно"),
        default=True,
        db_index=True,
    )
    sort_order = models.PositiveIntegerField(
        _("Порядок сортировки"),
        default=0,
    )

    class Meta:
        verbose_name = _("Должность")
        verbose_name_plural = _("Должности")
        ordering = ("sort_order", "name_ru")

    def __str__(self) -> str:
        return self.name_ru


class AcademicDegree(BaseModel):
    """
    Учёная степень.
    """

    code = models.CharField(
        _("Код"),
        max_length=50,
        unique=True,
        db_index=True,
    )
    name_ru = models.CharField(
        _("Название на русском"),
        max_length=255,
    )
    name_uz = models.CharField(
        _("Название на узбекском"),
        max_length=255,
    )
    short_name_ru = models.CharField(
        _("Сокращение на русском"),
        max_length=100,
        blank=True,
    )
    short_name_uz = models.CharField(
        _("Сокращение на узбекском"),
        max_length=100,
        blank=True,
    )
    is_active = models.BooleanField(
        _("Активно"),
        default=True,
        db_index=True,
    )
    sort_order = models.PositiveIntegerField(
        _("Порядок сортировки"),
        default=0,
    )

    class Meta:
        verbose_name = _("Учёная степень")
        verbose_name_plural = _("Учёные степени")
        ordering = ("sort_order", "name_ru")

    def __str__(self) -> str:
        return self.short_name_ru or self.name_ru


class AcademicTitle(BaseModel):
    """
    Учёное звание.
    """

    code = models.CharField(
        _("Код"),
        max_length=50,
        unique=True,
        db_index=True,
    )
    name_ru = models.CharField(
        _("Название на русском"),
        max_length=255,
    )
    name_uz = models.CharField(
        _("Название на узбекском"),
        max_length=255,
    )
    short_name_ru = models.CharField(
        _("Сокращение на русском"),
        max_length=100,
        blank=True,
    )
    short_name_uz = models.CharField(
        _("Сокращение на узбекском"),
        max_length=100,
        blank=True,
    )
    is_active = models.BooleanField(
        _("Активно"),
        default=True,
        db_index=True,
    )
    sort_order = models.PositiveIntegerField(
        _("Порядок сортировки"),
        default=0,
    )

    class Meta:
        verbose_name = _("Учёное звание")
        verbose_name_plural = _("Учёные звания")
        ordering = ("sort_order", "name_ru")

    def __str__(self) -> str:
        return self.short_name_ru or self.name_ru


class StaffMember(BaseModel):
    """
    Карточка преподавателя или сотрудника.

    Один пользователь системы может иметь не более одной
    кадровой карточки.
    """

    class Gender(models.TextChoices):
        MALE = "male", _("Мужской")
        FEMALE = "female", _("Женский")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Пользователь"),
        related_name="staff_profile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    personnel_number = models.CharField(
        _("Табельный номер"),
        max_length=50,
        unique=True,
        db_index=True,
    )
    last_name = models.CharField(
        _("Фамилия"),
        max_length=150,
    )
    first_name = models.CharField(
        _("Имя"),
        max_length=150,
    )
    middle_name = models.CharField(
        _("Отчество"),
        max_length=150,
        blank=True,
    )
    gender = models.CharField(
        _("Пол"),
        max_length=10,
        choices=Gender.choices,
        blank=True,
    )
    birth_date = models.DateField(
        _("Дата рождения"),
        null=True,
        blank=True,
    )
    phone = models.CharField(
        _("Телефон"),
        max_length=30,
        blank=True,
    )
    email = models.EmailField(
        _("Электронная почта"),
        blank=True,
    )
    academic_degree = models.ForeignKey(
        AcademicDegree,
        verbose_name=_("Учёная степень"),
        related_name="staff_members",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    academic_title = models.ForeignKey(
        AcademicTitle,
        verbose_name=_("Учёное звание"),
        related_name="staff_members",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    degree_awarded_date = models.DateField(
        _("Дата присуждения учёной степени"),
        null=True,
        blank=True,
    )
    title_awarded_date = models.DateField(
        _("Дата присвоения учёного звания"),
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        _("Работает"),
        default=True,
        db_index=True,
    )
    notes = models.TextField(
        _("Примечание"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Преподаватель или сотрудник")
        verbose_name_plural = _("Преподаватели и сотрудники")
        ordering = (
            "last_name",
            "first_name",
            "middle_name",
        )

    @property
    def full_name(self) -> str:
        return " ".join(
            part
            for part in (
                self.last_name,
                self.first_name,
                self.middle_name,
            )
            if part
        )

    @property
    def has_academic_degree(self) -> bool:
        return self.academic_degree_id is not None

    @property
    def has_academic_title(self) -> bool:
        return self.academic_title_id is not None

    def clean(self):
        super().clean()

        if (
            self.degree_awarded_date
            and not self.academic_degree_id
        ):
            raise ValidationError(
                {
                    "degree_awarded_date": _(
                        "Дата присуждения не может быть указана "
                        "без учёной степени."
                    )
                }
            )

        if (
            self.title_awarded_date
            and not self.academic_title_id
        ):
            raise ValidationError(
                {
                    "title_awarded_date": _(
                        "Дата присвоения не может быть указана "
                        "без учёного звания."
                    )
                }
            )

        if self.birth_date and self.birth_date > timezone.localdate():
            raise ValidationError(
                {
                    "birth_date": _(
                        "Дата рождения не может быть в будущем."
                    )
                }
            )

    def __str__(self) -> str:
        return self.full_name

class StaffEmployment(BaseModel):
    """
    Назначение сотрудника на должность в кафедре.

    Один сотрудник может иметь несколько назначений:
    основное место работы, внутреннее или внешнее
    совместительство.
    """

    class EmploymentType(models.TextChoices):
        PRIMARY = "primary", _("Основное место работы")
        INTERNAL_PART_TIME = (
            "internal_part_time",
            _("Внутреннее совместительство"),
        )
        EXTERNAL_PART_TIME = (
            "external_part_time",
            _("Внешнее совместительство"),
        )
        HOURLY = "hourly", _("Почасовая работа")

    staff_member = models.ForeignKey(
        StaffMember,
        verbose_name=_("Сотрудник"),
        related_name="employments",
        on_delete=models.PROTECT,
    )
    department = models.ForeignKey(
        Department,
        verbose_name=_("Кафедра"),
        related_name="staff_employments",
        on_delete=models.PROTECT,
    )
    position = models.ForeignKey(
        StaffPosition,
        verbose_name=_("Должность"),
        related_name="staff_employments",
        on_delete=models.PROTECT,
    )
    employment_type = models.CharField(
        _("Вид занятости"),
        max_length=30,
        choices=EmploymentType.choices,
        default=EmploymentType.PRIMARY,
        db_index=True,
    )
    rate = models.DecimalField(
        _("Размер ставки"),
        max_digits=4,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[
            MinValueValidator(Decimal("0.01")),
            MaxValueValidator(Decimal("3.00")),
        ],
    )
    start_date = models.DateField(
        _("Дата начала работы"),
    )
    end_date = models.DateField(
        _("Дата окончания работы"),
        null=True,
        blank=True,
    )
    is_primary = models.BooleanField(
        _("Основное назначение"),
        default=False,
        db_index=True,
    )
    is_active = models.BooleanField(
        _("Активно"),
        default=True,
        db_index=True,
    )
    document_number = models.CharField(
        _("Номер приказа"),
        max_length=100,
        blank=True,
    )
    document_date = models.DateField(
        _("Дата приказа"),
        null=True,
        blank=True,
    )
    notes = models.TextField(
        _("Примечание"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Трудовое назначение")
        verbose_name_plural = _("Трудовые назначения")
        ordering = (
            "staff_member__last_name",
            "-is_primary",
            "-start_date",
        )
        constraints = [
            models.UniqueConstraint(
                fields=("staff_member",),
                condition=Q(
                    is_primary=True,
                    is_active=True,
                    is_archived=False,
                ),
                name="unique_active_primary_staff_employment",
            ),
        ]

    def clean(self):
        super().clean()

        if self.end_date and self.end_date < self.start_date:
            raise ValidationError(
                {
                    "end_date": _(
                        "Дата окончания не может быть раньше "
                        "даты начала."
                    )
                }
            )

        if self.department_id:
            if self.department.is_archived:
                raise ValidationError(
                    {
                        "department": _(
                            "Нельзя выбрать архивную кафедру."
                        )
                    }
                )

            if not self.department.is_active:
                raise ValidationError(
                    {
                        "department": _(
                            "Нельзя выбрать неактивную кафедру."
                        )
                    }
                )

        if self.position_id and not self.position.is_active:
            raise ValidationError(
                {
                    "position": _(
                        "Нельзя выбрать неактивную должность."
                    )
                }
            )

        if self.is_primary:
            self.employment_type = self.EmploymentType.PRIMARY

    def __str__(self) -> str:
        return (
            f"{self.staff_member} — "
            f"{self.position}, {self.rate} ставки"
        )

    def get_workload_norm(self, academic_year):
        """
        Возвращает точную норму для назначения.

        Результат может быть None, если подходящая норма
        в справочнике не установлена.
        """

        return WorkloadNorm.objects.filter(
            academic_year=academic_year,
            rate=self.rate,
            has_academic_degree=(
                self.staff_member.has_academic_degree
            ),
            has_academic_title=(
                self.staff_member.has_academic_title
            ),
            is_active=True,
        ).first()

    def get_recommended_annual_hours(self, academic_year):
        norm = self.get_workload_norm(academic_year)

        if norm is None:
            return None

        return norm.annual_hours

class WorkloadNorm(BaseModel):
    """
    Информационная годовая норма учебной нагрузки.

    Норма зависит от:
    - учебного года;
    - размера ставки;
    - наличия учёной степени;
    - наличия учёного звания.

    Запись не накладывает жёсткого ограничения на
    фактическую нагрузку преподавателя.
    """

    academic_year = models.ForeignKey(
        AcademicYear,
        verbose_name=_("Учебный год"),
        related_name="workload_norms",
        on_delete=models.PROTECT,
    )
    rate = models.DecimalField(
        _("Размер ставки"),
        max_digits=4,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
            MaxValueValidator(Decimal("3.00")),
        ],
    )
    has_academic_degree = models.BooleanField(
        _("Наличие учёной степени"),
        default=False,
    )
    has_academic_title = models.BooleanField(
        _("Наличие учёного звания"),
        default=False,
    )
    annual_hours = models.DecimalField(
        _("Годовая норма часов"),
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("10000.00")),
        ],
    )
    is_active = models.BooleanField(
        _("Активно"),
        default=True,
        db_index=True,
    )
    notes = models.TextField(
        _("Примечание"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Норма учебной нагрузки")
        verbose_name_plural = _("Нормы учебной нагрузки")
        ordering = (
            "-academic_year__start_year",
            "-rate",
            "-has_academic_degree",
            "-has_academic_title",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "academic_year",
                    "rate",
                    "has_academic_degree",
                    "has_academic_title",
                ),
                name="unique_workload_norm_combination",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.academic_year}: {self.rate} ставки, "
            f"{self.annual_hours} часов"
        )