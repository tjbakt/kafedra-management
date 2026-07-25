from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel
from apps.organizations.models import Department, Faculty, University


class AcademicYear(BaseModel):
    """
    Учебный год, например 2025/2026.
    """

    start_year = models.PositiveSmallIntegerField(
        _("Год начала"),
        validators=[
            MinValueValidator(2000),
            MaxValueValidator(2200),
        ],
    )
    end_year = models.PositiveSmallIntegerField(
        _("Год окончания"),
        validators=[
            MinValueValidator(2001),
            MaxValueValidator(2201),
        ],
    )
    is_current = models.BooleanField(
        _("Текущий учебный год"),
        default=False,
        db_index=True,
    )
    is_active = models.BooleanField(
        _("Активен"),
        default=True,
        db_index=True,
    )

    class Meta:
        verbose_name = _("Учебный год")
        verbose_name_plural = _("Учебные годы")
        ordering = ("-start_year",)
        constraints = [
            models.UniqueConstraint(
                fields=("start_year", "end_year"),
                name="unique_academic_year_range",
            ),
            models.UniqueConstraint(
                fields=("is_current",),
                condition=Q(is_current=True, is_archived=False),
                name="unique_current_academic_year",
            ),
        ]

    def clean(self):
        super().clean()

        if self.end_year != self.start_year + 1:
            raise ValidationError(
                {
                    "end_year": _(
                        "Год окончания должен следовать "
                        "за годом начала."
                    )
                }
            )

    @property
    def name(self) -> str:
        return f"{self.start_year}/{self.end_year}"

    def __str__(self) -> str:
        return self.name


class EducationLevel(BaseModel):
    """
    Академическая степень: бакалавриат или магистратура.
    """

    class Code(models.TextChoices):
        BACHELOR = "bachelor", _("Бакалавриат")
        MASTER = "master", _("Магистратура")

    code = models.CharField(
        _("Код"),
        max_length=20,
        choices=Code.choices,
        unique=True,
    )
    name_ru = models.CharField(
        _("Название на русском"),
        max_length=100,
    )
    name_uz = models.CharField(
        _("Название на узбекском"),
        max_length=100,
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
        verbose_name = _("Академическая степень")
        verbose_name_plural = _("Академические степени")
        ordering = ("sort_order", "name_ru")

    def __str__(self) -> str:
        return self.name_ru


class StudyForm(BaseModel):
    """
    Форма обучения.
    """

    class Code(models.TextChoices):
        FULL_TIME = "full_time", _("Дневная")
        PART_TIME = "part_time", _("Заочная")
        EVENING = "evening", _("Вечерняя")
        DISTANCE = "distance", _("Дистанционная")

    code = models.CharField(
        _("Код"),
        max_length=20,
        choices=Code.choices,
        unique=True,
    )
    name_ru = models.CharField(
        _("Название на русском"),
        max_length=100,
    )
    name_uz = models.CharField(
        _("Название на узбекском"),
        max_length=100,
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
        verbose_name = _("Форма обучения")
        verbose_name_plural = _("Формы обучения")
        ordering = ("sort_order", "name_ru")

    def __str__(self) -> str:
        return self.name_ru


class EducationDuration(BaseModel):
    """
    Нормативная продолжительность обучения для сочетания
    академической степени и формы обучения.

    Значения хранятся в справочнике и могут изменяться
    в будущем без изменения программного кода.
    """

    education_level = models.ForeignKey(
        EducationLevel,
        verbose_name=_("Академическая степень"),
        related_name="durations",
        on_delete=models.PROTECT,
    )
    study_form = models.ForeignKey(
        StudyForm,
        verbose_name=_("Форма обучения"),
        related_name="durations",
        on_delete=models.PROTECT,
    )
    duration_months = models.PositiveSmallIntegerField(
        _("Продолжительность в месяцах"),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(120),
        ],
    )
    semesters_count = models.PositiveSmallIntegerField(
        _("Количество семестров"),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(20),
        ],
    )
    is_active = models.BooleanField(
        _("Активно"),
        default=True,
        db_index=True,
    )

    class Meta:
        verbose_name = _("Продолжительность обучения")
        verbose_name_plural = _("Продолжительность обучения")
        ordering = (
            "education_level__sort_order",
            "study_form__sort_order",
        )
        constraints = [
            models.UniqueConstraint(
                fields=("education_level", "study_form"),
                name="unique_level_study_form_duration",
            ),
        ]

    def clean(self):
        super().clean()

        if self.duration_months and self.semesters_count:
            expected_months = self.semesters_count * 6

            if self.duration_months != expected_months:
                raise ValidationError(
                    {
                        "duration_months": _(
                            "Продолжительность должна соответствовать "
                            "количеству семестров: один семестр равен "
                            "шести месяцам."
                        )
                    }
                )

    def __str__(self) -> str:
        return (
            f"{self.education_level} — "
            f"{self.study_form}: "
            f"{self.semesters_count} сем."
        )


class AcademicSemester(BaseModel):
    """
    Конкретный осенний или весенний семестр учебного года.
    """

    class Season(models.TextChoices):
        AUTUMN = "autumn", _("Осенний")
        SPRING = "spring", _("Весенний")

    academic_year = models.ForeignKey(
        AcademicYear,
        verbose_name=_("Учебный год"),
        related_name="semesters",
        on_delete=models.PROTECT,
    )
    season = models.CharField(
        _("Сезон"),
        max_length=10,
        choices=Season.choices,
    )
    start_date = models.DateField(
        _("Дата начала"),
    )
    end_date = models.DateField(
        _("Дата окончания"),
    )
    is_current = models.BooleanField(
        _("Текущий семестр"),
        default=False,
        db_index=True,
    )
    is_active = models.BooleanField(
        _("Активен"),
        default=True,
        db_index=True,
    )

    class Meta:
        verbose_name = _("Академический семестр")
        verbose_name_plural = _("Академические семестры")
        ordering = (
            "-academic_year__start_year",
            "season",
        )
        constraints = [
            models.UniqueConstraint(
                fields=("academic_year", "season"),
                name="unique_season_per_academic_year",
            ),
            models.UniqueConstraint(
                fields=("is_current",),
                condition=Q(is_current=True, is_archived=False),
                name="unique_current_academic_semester",
            ),
        ]

    def clean(self):
        super().clean()

        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError(
                    {
                        "end_date": _(
                            "Дата окончания должна быть позже даты начала."
                        )
                    }
                )

        if not self.academic_year_id or not self.start_date:
            return

        if self.season == self.Season.AUTUMN:
            if self.start_date.year != self.academic_year.start_year:
                raise ValidationError(
                    {
                        "start_date": _(
                            "Осенний семестр должен начинаться "
                            "в году начала учебного года."
                        )
                    }
                )

        if self.season == self.Season.SPRING:
            if self.start_date.year != self.academic_year.end_year:
                raise ValidationError(
                    {
                        "start_date": _(
                            "Весенний семестр должен начинаться "
                            "в году окончания учебного года."
                        )
                    }
                )

    def __str__(self) -> str:
        return f"{self.academic_year} — {self.get_season_display()}"


class StudyProgram(BaseModel):
    """
    Направление обучения.

    Профилирующая кафедра определяется для направления,
    а не непосредственно для группы.
    """

    university = models.ForeignKey(
        University,
        verbose_name=_("Университет"),
        related_name="study_programs",
        on_delete=models.PROTECT,
    )
    education_level = models.ForeignKey(
        EducationLevel,
        verbose_name=_("Академическая степень"),
        related_name="study_programs",
        on_delete=models.PROTECT,
    )
    code = models.CharField(
        _("Код направления"),
        max_length=50,
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
    profiling_department = models.ForeignKey(
        Department,
        verbose_name=_("Профилирующая кафедра"),
        related_name="profiled_study_programs",
        on_delete=models.PROTECT,
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
        verbose_name = _("Направление обучения")
        verbose_name_plural = _("Направления обучения")
        ordering = (
            "education_level__sort_order",
            "code",
            "name_ru",
        )
        constraints = [
            models.UniqueConstraint(
                fields=("university", "education_level", "code"),
                name="unique_study_program_code",
            ),
        ]

    def clean(self):
        super().clean()

        if not self.profiling_department_id or not self.university_id:
            return

        department_university_id = (
            self.profiling_department.faculty.university_id
        )

        if department_university_id != self.university_id:
            raise ValidationError(
                {
                    "profiling_department": _(
                        "Профилирующая кафедра должна относиться "
                        "к выбранному университету."
                    )
                }
            )

        if self.profiling_department.is_archived:
            raise ValidationError(
                {
                    "profiling_department": _(
                        "Нельзя выбрать архивную кафедру."
                    )
                }
            )

    def __str__(self) -> str:
        return f"{self.code} — {self.name_ru}"


class StudentGroup(BaseModel):
    """
    Учебная группа.

    faculty определяет факультет или отделение группы.
    profiling_department определяется через study_program.
    """

    academic_year_admission = models.ForeignKey(
        AcademicYear,
        verbose_name=_("Учебный год поступления"),
        related_name="admitted_groups",
        on_delete=models.PROTECT,
    )
    faculty = models.ForeignKey(
        Faculty,
        verbose_name=_("Факультет или отделение"),
        related_name="student_groups",
        on_delete=models.PROTECT,
    )
    study_program = models.ForeignKey(
        StudyProgram,
        verbose_name=_("Направление обучения"),
        related_name="student_groups",
        on_delete=models.PROTECT,
    )
    study_form = models.ForeignKey(
        StudyForm,
        verbose_name=_("Форма обучения"),
        related_name="student_groups",
        on_delete=models.PROTECT,
    )
    code = models.CharField(
        _("Код группы"),
        max_length=50,
        unique=True,
        db_index=True,
    )
    student_count = models.PositiveSmallIntegerField(
        _("Количество студентов"),
        default=0,
        validators=[
            MaxValueValidator(1000),
        ],
    )
    subgroup_count = models.PositiveSmallIntegerField(
        _("Количество подгрупп"),
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(20),
        ],
    )
    is_active = models.BooleanField(
        _("Активна"),
        default=True,
        db_index=True,
    )
    graduation_academic_year = models.ForeignKey(
        AcademicYear,
        verbose_name=_("Плановый учебный год выпуска"),
        related_name="graduating_groups",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    notes = models.TextField(
        _("Примечание"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Учебная группа")
        verbose_name_plural = _("Учебные группы")
        ordering = (
            "-academic_year_admission__start_year",
            "code",
        )

    def clean(self):
        super().clean()

        if self.faculty_id and self.study_program_id:
            if self.faculty.university_id != self.study_program.university_id:
                raise ValidationError(
                    {
                        "faculty": _(
                            "Факультет группы и направление обучения "
                            "должны относиться к одному университету."
                        )
                    }
                )

        if (
            self.study_program_id
            and self.study_form_id
            and not EducationDuration.objects.filter(
                education_level=self.study_program.education_level,
                study_form=self.study_form,
                is_active=True,
            ).exists()
        ):
            raise ValidationError(
                {
                    "study_form": _(
                        "Для выбранной степени и формы обучения "
                        "не задана нормативная продолжительность."
                    )
                }
            )

        if (
            self.graduation_academic_year_id
            and self.academic_year_admission_id
            and self.graduation_academic_year.start_year
            <= self.academic_year_admission.start_year
        ):
            raise ValidationError(
                {
                    "graduation_academic_year": _(
                        "Учебный год выпуска должен быть позже "
                        "учебного года поступления."
                    )
                }
            )

    @property
    def profiling_department(self):
        return self.study_program.profiling_department

    @property
    def profiling_department_faculty(self):
        return self.study_program.profiling_department.faculty

    def __str__(self) -> str:
        return self.code