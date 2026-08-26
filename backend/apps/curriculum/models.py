from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.academics.models import (
    AcademicYear,
    EducationDuration,
    StudyForm,
    StudyProgram,
)
from apps.common.models import BaseModel
from apps.organizations.models import Department


class Discipline(BaseModel):
    """
    Общий справочник учебных дисциплин.
    """

    code = models.CharField(
        _("Код дисциплины"),
        max_length=50,
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
    default_department = models.ForeignKey(
        Department,
        verbose_name=_("Кафедра по умолчанию"),
        related_name="default_disciplines",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text=_(
            "Кафедра, которая обычно обеспечивает дисциплину. "
            "В конкретном учебном плане её можно изменить."
        ),
    )
    workload_types = models.ManyToManyField(
        "WorkloadType",
        verbose_name=_("Допустимые виды учебной работы"),
        related_name="disciplines",
        blank=True,
        help_text=_(
            "Виды работы, которые могут использоваться "
            "для данной дисциплины в учебном плане."
        ),
    )

    is_active = models.BooleanField(
        _("Активна"),
        default=True,
        db_index=True,
    )
    sort_order = models.PositiveIntegerField(
        _("Порядок сортировки"),
        default=0,
    )

    class Meta:
        verbose_name = _("Дисциплина")
        verbose_name_plural = _("Дисциплины")
        ordering = ("sort_order", "name_ru")

    def __str__(self) -> str:
        return f"{self.code} — {self.name_ru}"

class WorkloadType(BaseModel):
    """
    Вид учебной или методической работы.
    """

    class Code(models.TextChoices):
        LECTURE = "lecture", _("Лекции")
        PRACTICE = "practice", _("Практические занятия")
        LABORATORY = "laboratory", _("Лабораторные занятия")
        SEMINAR = "seminar", _("Семинарские занятия")
        CONSULTATION = "consultation", _("Консультации")
        EXAM = "exam", _("Экзамен")
        CREDIT = "credit", _("Зачёт")
        COURSE_WORK = "course_work", _("Курсовая работа")
        COURSE_PROJECT = "course_project", _("Курсовой проект")
        COURSE_WORK_SUPERVISION = ( "course_work_supervision", _("Руководство курсовой работой"), )
        COURSE_PROJECT_SUPERVISION = ( "course_project_supervision", _("Руководство курсовым проектом"), )
        COURSE_WORK_DEFENSE = ( "course_work_defense", _("Защита курсовой работы"), )
        COURSE_PROJECT_DEFENSE = ( "course_project_defense", _("Защита курсового проекта"), )

        COURSE_WORK_PROJECT_DEFENSE = ( "course_work_project_defense", _("Защита курсовой работы/проекта"), )

        SCIENTIFIC_PRACTICE_SUPERVISION = ( "scientific_practice_supervision", _("Руководство научной практикой"), )
        QUALIFICATION_PRACTICE_SUPERVISION = ( "qualification_practice_supervision", _("Руководство квалификационной практикой"), )
        MASTER_DISSERTATION_SUPERVISION = ( "master_dissertation_supervision", _("Руководство магистерской диссертацией"), )
        MASTER_DISSERTATION_DEFENSE = ( "master_dissertation_defense", _("Защита магистерской диссертации"), )
        GRADUATION_WORK_SUPERVISION = ( "graduation_work_supervision", _("Руководство выпускной квалификационной работой"), )
        GRADUATION_WORK_DEFENSE = ( "graduation_work_defense", _("Защита выпускной квалификационной работы"), )
        RATING = ( "rating", _("Рейтинг"), )
        INDEPENDENT_WORK = ( "independent_work", _("Самостоятельная работа"), )
        OTHER = ( "other", _("Другой вид работы"), )

    class CalculationMode(models.TextChoices):
        FIXED = "fixed", _("Фиксированные часы")
        PER_GROUP = "per_group", _("На учебную группу")
        PER_SUBGROUP = "per_subgroup", _("На подгруппу")
        PER_STUDENT = "per_student", _("На одного студента")

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
    calculation_mode = models.CharField(
        _("Способ расчёта по умолчанию"),
        max_length=20,
        choices=CalculationMode.choices,
        default=CalculationMode.PER_GROUP,
    )
    is_classroom = models.BooleanField(
        _("Аудиторная работа"),
        default=True,
    )
    is_teaching_load = models.BooleanField(
        _("Включать в нагрузку преподавателя"),
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
        verbose_name = _("Вид учебной работы")
        verbose_name_plural = _("Виды учебной работы")
        ordering = ("sort_order", "name_ru")

    class ReportCategory(models.TextChoices):
        LECTURE = "lecture", _("Лекции")
        PRACTICE = "practice", _("Практические занятия")
        LABORATORY = "laboratory", _("Лабораторные занятия")
        COURSE_WORK_SUPERVISION = ( "course_work_supervision", _("Руководство курсовой работой"), )
        COURSE_PROJECT_SUPERVISION = ( "course_project_supervision", _("Руководство курсовым проектом"), )
        COURSE_WORK_DEFENSE = ( "course_work_defense", _("Защита курсовой работы"), )
        COURSE_PROJECT_DEFENSE = ( "course_project_defense", _("Защита курсовой проекта"), )
        SCIENTIFIC_PRACTICE = ( "scientific_practice", _("Научная практика"), )
        QUALIFICATION_PRACTICE = ( "qualification_practice", _("Квалификационная практика"), )
        MASTER_DISSERTATION_SUPERVISION = ( "master_dissertation_supervision", _("Руководство магистерской диссертацией"), )
        MASTER_DISSERTATION_DEFENSE = ( "master_dissertation_defense", _("Защита магистерской диссертации"), )
        GRADUATION_WORK_SUPERVISION = ( "graduation_work_supervision", _("Руководство выпускной квалификационной работой"), )
        GRADUATION_WORK_DEFENSE = ( "graduation_work_defense", _("Защита выпускной квалификационной работы"), )
        RATING = "rating", _("Рейтинг")
        OTHER = "other", _("Другое")

    report_category = models.CharField(
        _("Категория для отчётов"),
        max_length=50,
        choices=ReportCategory.choices,
        default=ReportCategory.OTHER,
        db_index=True,
    )

    ANNUAL_NORM_CODES = frozenset(
        {
            Code.RATING,

            Code.COURSE_WORK_SUPERVISION,
            Code.COURSE_WORK_DEFENSE,

            Code.COURSE_PROJECT_SUPERVISION,
            Code.COURSE_PROJECT_DEFENSE,

            Code.SCIENTIFIC_PRACTICE_SUPERVISION,
            Code.QUALIFICATION_PRACTICE_SUPERVISION,

            Code.GRADUATION_WORK_SUPERVISION,
            Code.GRADUATION_WORK_DEFENSE,

            Code.MASTER_DISSERTATION_SUPERVISION,
            Code.MASTER_DISSERTATION_DEFENSE,
        }
    )

    WEEKLY_NORM_CODES = frozenset(
        {
            Code.SCIENTIFIC_PRACTICE_SUPERVISION,
            Code.QUALIFICATION_PRACTICE_SUPERVISION,
        }
    )

    PAIRED_CODES = {
        Code.COURSE_WORK_SUPERVISION:
            Code.COURSE_WORK_DEFENSE,

        Code.COURSE_WORK_DEFENSE:
            Code.COURSE_WORK_SUPERVISION,

        Code.COURSE_PROJECT_SUPERVISION:
            Code.COURSE_PROJECT_DEFENSE,

        Code.COURSE_PROJECT_DEFENSE:
            Code.COURSE_PROJECT_SUPERVISION,

        Code.GRADUATION_WORK_SUPERVISION:
            Code.GRADUATION_WORK_DEFENSE,

        Code.GRADUATION_WORK_DEFENSE:
            Code.GRADUATION_WORK_SUPERVISION,

        Code.MASTER_DISSERTATION_SUPERVISION:
            Code.MASTER_DISSERTATION_DEFENSE,

        Code.MASTER_DISSERTATION_DEFENSE:
            Code.MASTER_DISSERTATION_SUPERVISION,
    }

    @property
    def uses_annual_norm(self) -> bool:
        return (
            self.code
            in self.ANNUAL_NORM_CODES
        )

    @property
    def uses_weekly_norm(self) -> bool:
        """
        Коэффициент задаётся в часах
        на одну неделю одной учебной группы.
        """
        return (
                self.code
                in self.WEEKLY_NORM_CODES
        )

    @property
    def paired_code(self):
        return self.PAIRED_CODES.get(
            self.code
        )

    #
    # Оставляем для совместимости
    # существующего frontend.
    #
    @property
    def uses_curriculum_rule(self) -> bool:
        return self.uses_annual_norm

    CURRICULUM_RULE_CATEGORIES = frozenset(
        {
            ReportCategory.RATING,
            ReportCategory.COURSE_WORK_SUPERVISION,
            ReportCategory.COURSE_PROJECT_SUPERVISION,
            ReportCategory.COURSE_WORK_DEFENSE,
            ReportCategory.COURSE_PROJECT_DEFENSE,
            ReportCategory.MASTER_DISSERTATION_SUPERVISION,
            ReportCategory.MASTER_DISSERTATION_DEFENSE,
            ReportCategory.GRADUATION_WORK_SUPERVISION,
            ReportCategory.GRADUATION_WORK_DEFENSE,
        }
    )

    def __str__(
            self,
    ) -> str:
        return self.name_ru

class AcademicYearWorkloadNorm(BaseModel):
    """
    Коэффициент/базовые часы вида работы
    на конкретный учебный год.

    Примеры:

    рейтинг:
        0.25 часа * число студентов

    руководство КР:
        2 часа * число студентов

    защита КР:
        0.2 часа * число студентов

    руководство КП:
        3 часа * число студентов
    """

    academic_year = models.ForeignKey(
        AcademicYear,
        verbose_name=_("Учебный год"),
        related_name="curriculum_workload_norms",
        on_delete=models.CASCADE,
    )

    workload_type = models.ForeignKey(
        WorkloadType,
        verbose_name=_("Вид учебной работы"),
        related_name="academic_year_norms",
        on_delete=models.PROTECT,
    )

    coefficient = models.DecimalField(
        _("Коэффициент / базовые часы"),
        max_digits=10,
        decimal_places=4,
        validators=[
            MinValueValidator(
                Decimal("0.0000")
            )
        ],
    )

    is_active = models.BooleanField(
        _("Активна"),
        default=True,
        db_index=True,
    )

    notes = models.TextField(
        _("Примечание"),
        blank=True,
    )

    class Meta:
        verbose_name = _(
            "Норма учебной нагрузки"
        )

        verbose_name_plural = _(
            "Нормы учебной нагрузки"
        )

        ordering = (
            "-academic_year__start_year",
            "workload_type__sort_order",
        )

        constraints = [
            models.UniqueConstraint(
                fields=(
                    "academic_year",
                    "workload_type",
                ),
                name=(
                    "unique_workload_norm_"
                    "per_academic_year"
                ),
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.workload_type_id
            and not
            self.workload_type
            .uses_annual_norm
        ):
            raise ValidationError(
                {
                    "workload_type": _(
                        "Для данного вида работы "
                        "годовая норма не используется."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.academic_year}: "
            f"{self.workload_type.name_ru} "
            f"= {self.coefficient}"
        )

class AcademicYearCreditNorm(BaseModel):
    academic_year = models.OneToOneField(
        AcademicYear,
        verbose_name=_("Учебный год"),
        related_name="credit_norm",
        on_delete=models.CASCADE,
    )

    hours_per_credit = models.DecimalField(
        _("Количество часов в одном кредите"),
        max_digits=6,
        decimal_places=2,
        default=Decimal("30.00"),
        validators=[
            MinValueValidator(
                Decimal("0.01")
            )
        ],
    )

    notes = models.TextField(
        _("Примечание"),
        blank=True,
    )

    class Meta:
        verbose_name = _(
            "Норма академического кредита"
        )

        verbose_name_plural = _(
            "Нормы академического кредита"
        )

    def __str__(self):
        return (
            f"{self.academic_year}: "
            f"1 кредит = "
            f"{self.hours_per_credit} ч."
        )

class Curriculum(BaseModel):
    """
    Учебный план направления и формы обучения.

    Учебный год определяет начало действия версии плана.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", _("Черновик")
        APPROVED = "approved", _("Утверждён")
        ARCHIVED = "archived", _("Устаревшая версия")

    study_program = models.ForeignKey(
        StudyProgram,
        verbose_name=_("Направление обучения"),
        related_name="curricula",
        on_delete=models.PROTECT,
    )
    study_form = models.ForeignKey(
        StudyForm,
        verbose_name=_("Форма обучения"),
        related_name="curricula",
        on_delete=models.PROTECT,
    )
    effective_academic_year = models.ForeignKey(
        AcademicYear,
        verbose_name=_("Учебный год начала действия"),
        related_name="effective_curricula",
        on_delete=models.PROTECT,
    )
    code = models.CharField(
        _("Код учебного плана"),
        max_length=100,
        unique=True,
        db_index=True,
    )
    version = models.PositiveSmallIntegerField(
        _("Номер версии"),
        default=1,
    )
    status = models.CharField(
        _("Статус"),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    approved_at = models.DateField(
        _("Дата утверждения"),
        null=True,
        blank=True,
    )
    approval_document = models.CharField(
        _("Документ утверждения"),
        max_length=255,
        blank=True,
    )
    is_active = models.BooleanField(
        _("Активен"),
        default=True,
        db_index=True,
    )
    notes = models.TextField(
        _("Примечание"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Учебный план")
        verbose_name_plural = _("Учебные планы")
        ordering = (
            "-effective_academic_year__start_year",
            "study_program__code",
            "-version",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "study_program",
                    "study_form",
                    "effective_academic_year",
                    "version",
                ),
                name="unique_curriculum_version",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.status == self.Status.APPROVED
            and not self.approved_at
        ):
            raise ValidationError(
                {
                    "approved_at": _(
                        "Для утверждённого учебного плана "
                        "необходимо указать дату утверждения."
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
                        "Для степени направления и выбранной формы "
                        "не задана продолжительность обучения."
                    )
                }
            )

    @property
    def education_level(self):
        return self.study_program.education_level

    @property
    def semesters_count(self):
        duration = EducationDuration.objects.filter(
            education_level=self.study_program.education_level,
            study_form=self.study_form,
            is_active=True,
        ).first()

        return duration.semesters_count if duration else None

    def __str__(self) -> str:
        return f"{self.code} — {self.study_program}"

class CurriculumWorkloadRule(BaseModel):
    """
    Единая норма расчёта вида работы для всего учебного плана.

    Например: рейтинг = 0.5 часа на студента.

    Все дисциплины этого учебного плана, для которых включён рейтинг, используют именно эту норму.
    """

    curriculum = models.ForeignKey(
        Curriculum,
        verbose_name=_("Учебный план"),
        related_name="workload_rules",
        on_delete=models.CASCADE,
    )

    workload_type = models.ForeignKey(
        WorkloadType,
        verbose_name=_("Вид учебной работы"),
        related_name="curriculum_rules",
        on_delete=models.PROTECT,
    )

    calculation_mode = models.CharField(
        _("Способ расчёта"),
        max_length=20,
        choices=WorkloadType.CalculationMode.choices,
    )

    base_hours = models.DecimalField(
        _("Базовое количество часов"),
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal("0.00")
            )
        ],
    )

    students_per_unit = models.PositiveSmallIntegerField(
        _("Количество студентов на одну расчётную единицу"),
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        _("Активна"),
        default=True,
        db_index=True,
    )

    notes = models.TextField(
        _("Примечание"),
        blank=True,
    )

    class Meta:
        verbose_name = _( "Норма нагрузки учебного плана" )
        verbose_name_plural = _( "Нормы нагрузки учебного плана" )
        ordering = (
            "curriculum",
            "workload_type__sort_order",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "curriculum",
                    "workload_type",
                ),
                name=(
                    "unique_curriculum_"
                    "workload_rule"
                ),
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.workload_type_id
            and not
            self.workload_type
            .uses_curriculum_rule
        ):
            raise ValidationError(
                {
                    "workload_type": _(
                        "Для данного вида работы  не используется единая норма учебного плана."
                    )
                }
            )

        if (
            self.calculation_mode
            == WorkloadType
            .CalculationMode
            .PER_STUDENT
            and self.base_hours <= 0
        ):
            raise ValidationError(
                {
                    "base_hours": _(
                        "Для расчёта на студента количество часов должно быть больше нуля."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()

        result = super().save( *args, **kwargs,)

        #
        # Синхронизируем все уже добавленные нагрузки учебного плана.
        #
        CurriculumWorkload.all_objects.filter(
            curriculum_discipline__curriculum_id=(
                self.curriculum_id
            ),
            workload_type_id=(
                self.workload_type_id
            ),
            is_archived=False,
        ).update(
            calculation_mode=(
                self.calculation_mode
            ),
            base_hours=self.base_hours,
            students_per_unit=(
                self.students_per_unit
            ),
        )

        return result

    def __str__(self) -> str:
        return (
            f"{self.curriculum.code}: "
            f"{self.workload_type.name_ru}"
        )

class CurriculumDiscipline(BaseModel):
    """
    Дисциплина в определённом семестре учебного плана.
    """
    class ControlForm(models.TextChoices):
        NONE = "none", _("Без итогового контроля")
        EXAM = "exam", _("Экзамен")
        CREDIT = "credit", _("Зачёт")
        GRADED_CREDIT = "graded_credit", _("Дифференцированный зачёт")
        COURSE_WORK = "course_work", _("Курсовая работа")
        COURSE_PROJECT = "course_project", _("Курсовой проект")

    class ComponentType(models.TextChoices):
        REQUIRED = "required", _("Обязательная дисциплина")
        ELECTIVE = "elective", _("Дисциплина по выбору")
        OPTIONAL = "optional", _("Факультатив")

    curriculum = models.ForeignKey(
        Curriculum,
        verbose_name=_("Учебный план"),
        related_name="curriculum_disciplines",
        on_delete=models.CASCADE,
    )
    discipline = models.ForeignKey(
        Discipline,
        verbose_name=_("Дисциплина"),
        related_name="curriculum_entries",
        on_delete=models.PROTECT,
    )
    semester_number = models.PositiveSmallIntegerField(
        _("Номер семестра"),
        validators=[MinValueValidator(1)],
        db_index=True,
    )
    teaching_department = models.ForeignKey(
        Department,
        verbose_name=_("Обеспечивающая кафедра"),
        related_name="taught_curriculum_disciplines",
        on_delete=models.PROTECT,
    )
    component_type = models.CharField(
        _("Компонент учебного плана"),
        max_length=20,
        choices=ComponentType.choices,
        default=ComponentType.REQUIRED,
    )
    control_form = models.CharField(
        _("Форма итогового контроля"),
        max_length=20,
        choices=ControlForm.choices,
        default=ControlForm.NONE,
    )
    credits = models.DecimalField(
        _("Количество кредитов"),
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total_academic_hours = models.DecimalField(
        _("Общий объём академических часов"),
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    independent_hours = models.DecimalField(
        _("Часы самостоятельной работы"),
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    weeks_count = models.PositiveSmallIntegerField(
        _("Количество учебных недель"),
        default=15,
        validators=[MinValueValidator(1)],
    )
    is_active = models.BooleanField(
        _("Активна"),
        default=True,
        db_index=True,
    )
    notes = models.TextField(
        _("Примечание"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Дисциплина учебного плана")
        verbose_name_plural = _("Дисциплины учебного плана")
        ordering = (
            "curriculum",
            "semester_number",
            "discipline__name_ru",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "curriculum",
                    "discipline",
                    "semester_number",
                ),
                name="unique_discipline_per_curriculum_semester",
            ),
        ]

    @property
    def season(self) -> str:
        if self.semester_number % 2:
            return "autumn"

        return "spring"

    @property
    def season_name(self) -> str:
        if self.semester_number % 2:
            return _("Осенний")

        return _("Весенний")

    @property
    def planned_contact_hours(self):
        classroom_codes = (
            WorkloadType.Code.LECTURE,
            WorkloadType.Code.PRACTICE,
            WorkloadType.Code.LABORATORY,
            WorkloadType.Code.SEMINAR,
        )

        return sum(
            (
                item.base_hours
                for item
                in self.workload_items.filter(
                is_archived=False,
                is_active=True,
                workload_type__code__in=(
                    classroom_codes
                ),
            )
            ),
            Decimal("0.00"),
        )

    def clean(self):
        super().clean()

        if self.curriculum_id:
            semesters_count = self.curriculum.semesters_count

            if (
                semesters_count is not None
                and self.semester_number > semesters_count
            ):
                raise ValidationError(
                    {
                        "semester_number": _(
                            "Номер семестра превышает нормативное "
                            "количество семестров учебного плана."
                        )
                    }
                )

        if self.teaching_department_id:
            program_university_id = (
                self.curriculum.study_program.university_id
                if self.curriculum_id
                else None
            )
            department_university_id = (
                self.teaching_department.faculty.university_id
            )

            if (
                program_university_id
                and department_university_id
                != program_university_id
            ):
                raise ValidationError(
                    {
                        "teaching_department": _(
                            "Обеспечивающая кафедра должна относиться "
                            "к университету учебного плана."
                        )
                    }
                )

        if self.independent_hours > self.total_academic_hours:
            raise ValidationError(
                {
                    "independent_hours": _(
                        "Самостоятельные часы не могут превышать "
                        "общий объём дисциплины."
                    )
                }
            )

    def __str__(self) -> str:
        return (
            f"{self.curriculum.code}: "
            f"{self.discipline.name_ru}, "
            f"{self.semester_number} семестр"
        )

class CurriculumWorkload(BaseModel):
    """
    Плановый вид нагрузки дисциплины.

    base_hours — количество часов по учебному плану.
    calculation_mode определяет, как часы будут рассчитаны
    для конкретной группы.
    """

    curriculum_discipline = models.ForeignKey(
        CurriculumDiscipline,
        verbose_name=_("Дисциплина учебного плана"),
        related_name="workload_items",
        on_delete=models.CASCADE,
    )
    workload_type = models.ForeignKey(
        WorkloadType,
        verbose_name=_("Вид учебной работы"),
        related_name="curriculum_workloads",
        on_delete=models.PROTECT,
    )
    calculation_mode = models.CharField(
        _("Способ расчёта"),
        max_length=20,
        choices=WorkloadType.CalculationMode.choices,
    )
    base_hours = models.DecimalField(
        _("Базовое количество часов"),
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    students_per_unit = models.PositiveSmallIntegerField(
        _("Количество студентов на одну расчётную единицу"),
        null=True,
        blank=True,
        help_text=_(
            "Используется для некоторых видов расчёта "
            "по количеству студентов."
        ),
    )
    is_active = models.BooleanField(
        _("Активна"),
        default=True,
        db_index=True,
    )
    notes = models.TextField(
        _("Примечание"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Нагрузка дисциплины")
        verbose_name_plural = _("Нагрузка дисциплин")
        ordering = (
            "curriculum_discipline",
            "workload_type__sort_order",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "curriculum_discipline",
                    "workload_type",
                ),
                name="unique_workload_type_per_discipline",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.calculation_mode
            == WorkloadType.CalculationMode.PER_STUDENT
            and self.base_hours <= 0
        ):
            raise ValidationError(
                {
                    "base_hours": _(
                        "Для расчёта на одного студента значение "
                        "часов должно быть больше нуля."
                    )
                }
            )

    def calculate_hours(
        self,
        *,
        groups_count: int = 1,
        subgroups_count: int = 1,
        students_count: int = 0,
    ) -> Decimal:
        """
        Предварительный расчёт нагрузки.

        Позже этот метод будет использоваться при формировании
        фактической нагрузки кафедры.
        """

        if (
            self.calculation_mode
            == WorkloadType.CalculationMode.FIXED
        ):
            return self.base_hours

        if (
            self.calculation_mode
            == WorkloadType.CalculationMode.PER_GROUP
        ):
            return self.base_hours * Decimal(groups_count)

        if (
            self.calculation_mode
            == WorkloadType.CalculationMode.PER_SUBGROUP
        ):
            return self.base_hours * Decimal(subgroups_count)

        if (
            self.calculation_mode
            == WorkloadType.CalculationMode.PER_STUDENT
        ):
            return self.base_hours * Decimal(students_count)

        return Decimal("0.00")

    def __str__(self) -> str:
        return (
            f"{self.curriculum_discipline} — "
            f"{self.workload_type}"
        )