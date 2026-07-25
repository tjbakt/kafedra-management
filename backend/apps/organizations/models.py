from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel


class OrganizationBaseModel(BaseModel):
    """
    Общие поля организационных справочников.
    """

    code = models.CharField(
        _("Код"),
        max_length=30,
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
        _("Краткое название на русском"),
        max_length=100,
        blank=True,
    )
    short_name_uz = models.CharField(
        _("Краткое название на узбекском"),
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
        abstract = True


class University(OrganizationBaseModel):
    """
    Высшее образовательное учреждение.
    """

    address_ru = models.CharField(
        _("Адрес на русском"),
        max_length=500,
        blank=True,
    )
    address_uz = models.CharField(
        _("Адрес на узбекском"),
        max_length=500,
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
    website = models.URLField(
        _("Веб-сайт"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Университет")
        verbose_name_plural = _("Университеты")
        ordering = (
            "sort_order",
            "name_ru",
        )

    def __str__(self):
        return self.name_ru


class Faculty(OrganizationBaseModel):
    """
    Факультет или учебное отделение университета.
    """

    class FacultyType(models.TextChoices):
        STANDARD = "standard", _("Обычный факультет")
        MAGISTRACY = "magistracy", _("Отделение магистратуры")

    university = models.ForeignKey(
        University,
        verbose_name=_("Университет"),
        related_name="faculties",
        on_delete=models.PROTECT,
    )
    faculty_type = models.CharField(
        _("Тип факультета"),
        max_length=20,
        choices=FacultyType.choices,
        default=FacultyType.STANDARD,
        db_index=True,
    )
    dean_name = models.CharField(
        _("Декан или руководитель"),
        max_length=255,
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

    class Meta:
        verbose_name = _("Факультет или отделение")
        verbose_name_plural = _("Факультеты и отделения")
        ordering = (
            "sort_order",
            "name_ru",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "university",
                    "name_ru",
                ),
                name="unique_faculty_name_ru_per_university",
            ),
            models.UniqueConstraint(
                fields=(
                    "university",
                    "name_uz",
                ),
                name="unique_faculty_name_uz_per_university",
            ),
        ]

    def __str__(self):
        return self.name_ru


class Department(OrganizationBaseModel):
    """
    Кафедра факультета.
    """

    faculty = models.ForeignKey(
        Faculty,
        verbose_name=_("Факультет"),
        related_name="departments",
        on_delete=models.PROTECT,
    )
    head_name = models.CharField(
        _("Заведующий кафедрой"),
        max_length=255,
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
    room = models.CharField(
        _("Аудитория или кабинет"),
        max_length=100,
        blank=True,
    )

    class Meta:
        verbose_name = _("Кафедра")
        verbose_name_plural = _("Кафедры")
        ordering = (
            "sort_order",
            "name_ru",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "faculty",
                    "name_ru",
                ),
                name="unique_department_name_ru_per_faculty",
            ),
            models.UniqueConstraint(
                fields=(
                    "faculty",
                    "name_uz",
                ),
                name="unique_department_name_uz_per_faculty",
            ),
        ]

    def clean(self):
        super().clean()

        if self.faculty_id and self.faculty.is_archived:
            raise ValidationError(
                {
                    "faculty": _(
                        "Нельзя привязать кафедру к архивному факультету."
                    )
                }
            )

    def __str__(self):
        return self.name_ru