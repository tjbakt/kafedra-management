from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel
from apps.organizations.models import University


def report_template_upload_to(instance, filename):
    return (
        f"report_templates/"
        f"{instance.template_type}/"
        f"{filename}"
    )


class ExcelReportTemplate(BaseModel):
    """
    Excel-шаблон формирования отчёта.

    Одновременно может существовать только один активный
    шаблон одного типа для университета.
    """

    class Type(models.TextChoices):
        TEACHER_WORKLOAD = (
            "teacher_workload",
            _("Нагрузка преподавателя за учебный год"),
        )
        DEPARTMENT_WORKLOAD = (
            "department_workload",
            _("Общая нагрузка кафедры за учебный год"),
        )

    university = models.ForeignKey(
        University,
        verbose_name=_("Университет"),
        related_name="excel_report_templates",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text=_(
            "Если университет не указан, шаблон является общим."
        ),
    )
    template_type = models.CharField(
        _("Тип шаблона"),
        max_length=50,
        choices=Type.choices,
        db_index=True,
    )
    name = models.CharField(
        _("Название"),
        max_length=255,
    )
    version = models.PositiveIntegerField(
        _("Версия"),
        default=1,
    )
    file = models.FileField(
        _("Excel-файл"),
        upload_to=report_template_upload_to,
    )
    sheet_name = models.CharField(
        _("Название листа"),
        max_length=255,
        blank=True,
        help_text=_(
            "Если не указано, используется активный лист."
        ),
    )
    is_active = models.BooleanField(
        _("Активен"),
        default=True,
        db_index=True,
    )
    description = models.TextField(
        _("Описание"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Excel-шаблон отчёта")
        verbose_name_plural = _("Excel-шаблоны отчётов")
        ordering = (
            "template_type",
            "-version",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "university",
                    "template_type",
                ),
                condition=Q(
                    university__isnull=False,
                    is_active=True,
                    is_archived=False,
                ),
                name="unique_active_university_excel_template",
            ),
            models.UniqueConstraint(
                fields=("template_type",),
                condition=Q(
                    university__isnull=True,
                    is_active=True,
                    is_archived=False,
                ),
                name="unique_active_global_excel_template",
            ),
        ]

    def clean(self):
        super().clean()

        if self.file:
            filename = self.file.name.lower()

            if not filename.endswith(".xlsx"):
                raise ValidationError(
                    {
                        "file": (
                            "Допускаются только файлы формата .xlsx."
                        )
                    }
                )

    def __str__(self):
        scope = (
            self.university.name_ru
            if self.university_id
            else _("Общий шаблон")
        )

        return (
            f"{self.get_template_type_display()} — "
            f"{scope}, версия {self.version}"
        )