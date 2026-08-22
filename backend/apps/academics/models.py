from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from apps.common.models import BaseModel
from apps.organizations.models import Department, Faculty, University


class AcademicYear(BaseModel):
    """
    Учебный год, например 2025/2026.
    """

    class Status(models.TextChoices):
        OPEN = "open", _("Открыт")
        CLOSED = "closed", _("Закрыт")

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
    status = models.CharField(
        _("Статус"),
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    closed_at = models.DateTimeField(
        _("Дата закрытия"),
        null=True,
        blank=True,
        db_index=True,
    )
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Закрыл"),
        related_name="closed_academic_years",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    closing_comment = models.TextField(
        _("Комментарий при закрытии"),
        blank=True,
    )

    reopened_at = models.DateTimeField(
        _("Дата последнего открытия"),
        null=True,
        blank=True,
    )
    reopened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Повторно открыл"),
        related_name="reopened_academic_years",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    reopening_reason = models.TextField(
        _("Причина повторного открытия"),
        blank=True,
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
        if self.status == self.Status.CLOSED:
            if self.is_current:
                raise ValidationError(
                    {
                        "is_current": _(
                            "Закрытый учебный год не может "
                            "быть текущим."
                        )
                    }
                )

            if self.is_active:
                raise ValidationError(
                    {
                        "is_active": _(
                            "Закрытый учебный год не может "
                            "быть активным."
                        )
                    }
                )

            if self.closed_at is None:
                raise ValidationError(
                    {
                        "closed_at": _(
                            "Для закрытого учебного года "
                            "должна быть указана дата закрытия."
                        )
                    }
                )

        if (
                self.status == self.Status.OPEN
                and self.closed_at is not None
        ):
            raise ValidationError(
                {
                    "closed_at": _(
                        "Открытый учебный год не должен "
                        "содержать активную дату закрытия."
                    )
                }
            )

    @property
    def name(self) -> str:
        return f"{self.start_year}/{self.end_year}"

    @property
    def is_closed(self) -> bool:
        return self.status == self.Status.CLOSED

    @property
    def is_open(self) -> bool:
        return self.status == self.Status.OPEN

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
        null=True,
        blank=True,
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

    def get_education_duration(self):
        if (
            not self.study_program_id
            or not self.study_form_id
        ):
            return None

        return (
            EducationDuration.objects
            .filter(
                education_level=(
                    self.study_program
                    .education_level
                ),
                study_form=self.study_form,
                is_active=True,
                is_archived=False,
            )
            .first()
        )

    @property
    def study_years_count(self):
        duration = (
            self.get_education_duration()
        )

        if not duration:
            return None

        return (
            duration.semesters_count + 1
        ) // 2

    def course_number_for(
        self,
        academic_year,
    ):
        """
        Курс группы в конкретном
        учебном году.

        Поступление 2024/2025:
        2024/2025 -> 1 курс
        2025/2026 -> 2 курс
        2026/2027 -> 3 курс
        """

        if (
            not self
            .academic_year_admission_id
        ):
            return None

        difference = (
            academic_year.start_year
            - self
            .academic_year_admission
            .start_year
        )

        course = difference + 1

        years_count = (
            self.study_years_count
        )

        if (
            years_count is None
            or course < 1
            or course > years_count
        ):
            return None

        return course

    def semester_number_for(
        self,
        academic_semester,
    ):
        """
        Определяет номер семестра
        группы по году поступления.

        1 курс:
            осень -> 1
            весна -> 2

        2 курс:
            осень -> 3
            весна -> 4
        """

        course = (
            self.course_number_for(
                academic_semester
                .academic_year
            )
        )

        if course is None:
            return None

        semester_number = (
            (course - 1) * 2
        )

        if (
            academic_semester.season
            == AcademicSemester
            .Season
            .AUTUMN
        ):
            semester_number += 1
        else:
            semester_number += 2

        duration = (
            self.get_education_duration()
        )

        if (
            duration
            and semester_number
            > duration.semesters_count
        ):
            return None

        return semester_number

    @property
    def current_course_number(self):
        academic_year = (
            AcademicYear.objects
            .filter(
                is_current=True,
                is_archived=False,
            )
            .first()
        )

        if not academic_year:
            return None

        return self.course_number_for(
            academic_year
        )

    @property
    def current_semester_number(self):
        academic_semester = (
            AcademicSemester.objects
            .filter(
                is_current=True,
                is_archived=False,
            )
            .select_related(
                "academic_year"
            )
            .first()
        )

        if not academic_semester:
            return None

        return self.semester_number_for(
            academic_semester
        )

    @property
    def calculated_graduation_start_year(
        self,
    ):
        """
        Первый год планового
        учебного года выпуска.

        8 семестров = 4 учебных года.
        10 семестров = 5 учебных лет.
        9 семестров = 5 учебных лет.
        """

        if (
            not self
            .academic_year_admission_id
        ):
            return None

        years_count = (
            self.study_years_count
        )

        if years_count is None:
            return None

        return (
            self
            .academic_year_admission
            .start_year
            + years_count
            - 1
        )

    @property
    def calculated_graduation_academic_year(
        self,
    ):
        start_year = (
            self
            .calculated_graduation_start_year
        )

        if start_year is None:
            return None

        return (
            AcademicYear.objects
            .filter(
                start_year=start_year,
                end_year=start_year + 1,
                is_archived=False,
            )
            .first()
        )

    def sync_graduation_academic_year(
        self,
    ):
        calculated = (
            self
            .calculated_graduation_academic_year
        )

        if calculated:
            self.graduation_academic_year = (
                calculated
            )

    def save(
        self,
        *args,
        **kwargs,
    ):
        if (
            self.academic_year_admission_id
            and self.study_program_id
            and self.study_form_id
        ):
            self.sync_graduation_academic_year()

        return super().save(
            *args,
            **kwargs,
        )

    def __str__(self) -> str:
        return self.code