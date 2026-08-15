from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.academics.models import (
    AcademicSemester,
    AcademicYear,
    StudentGroup,
)
from apps.common.models import BaseModel
from apps.curriculum.models import (
    Curriculum,
    CurriculumDiscipline,
    CurriculumWorkload,
    WorkloadType,
)
from apps.organizations.models import Department


class GroupCurriculumAssignment(BaseModel):
    """
    Назначение учебного плана учебной группе.

    Обычно группа имеет один основной действующий учебный план,
    но история назначений сохраняется.
    """

    student_group = models.ForeignKey(
        StudentGroup,
        verbose_name=_("Учебная группа"),
        related_name="curriculum_assignments",
        on_delete=models.PROTECT,
    )
    curriculum = models.ForeignKey(
        Curriculum,
        verbose_name=_("Учебный план"),
        related_name="group_assignments",
        on_delete=models.PROTECT,
    )
    start_academic_year = models.ForeignKey(
        AcademicYear,
        verbose_name=_("Учебный год начала применения"),
        related_name="started_group_curricula",
        on_delete=models.PROTECT,
    )
    end_academic_year = models.ForeignKey(
        AcademicYear,
        verbose_name=_("Учебный год окончания применения"),
        related_name="ended_group_curricula",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    is_primary = models.BooleanField(
        _("Основной учебный план"),
        default=True,
        db_index=True,
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
        verbose_name = _("Учебный план группы")
        verbose_name_plural = _("Учебные планы групп")
        ordering = (
            "-start_academic_year__start_year",
            "student_group__code",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "student_group",
                    "curriculum",
                    "start_academic_year",
                ),
                name="unique_group_curriculum_assignment",
            ),
            models.UniqueConstraint(
                fields=("student_group",),
                condition=models.Q(
                    is_primary=True,
                    is_active=True,
                    is_archived=False,
                ),
                name="unique_active_primary_group_curriculum",
            ),
        ]

    def clean(self):
        super().clean()

        if not self.student_group_id or not self.curriculum_id:
            return

        if (
            self.student_group.study_program_id
            != self.curriculum.study_program_id
        ):
            raise ValidationError(
                {
                    "curriculum": _(
                        "Направление учебного плана не совпадает "
                        "с направлением учебной группы."
                    )
                }
            )

        if (
            self.student_group.study_form_id
            != self.curriculum.study_form_id
        ):
            raise ValidationError(
                {
                    "curriculum": _(
                        "Форма обучения учебного плана не совпадает "
                        "с формой обучения группы."
                    )
                }
            )

        if (
            self.end_academic_year_id
            and self.end_academic_year.start_year
            < self.start_academic_year.start_year
        ):
            raise ValidationError(
                {
                    "end_academic_year": _(
                        "Учебный год окончания не может быть раньше "
                        "учебного года начала."
                    )
                }
            )

    def __str__(self):
        return f"{self.student_group} — {self.curriculum.code}"

class GroupSemester(BaseModel):
    """
    Состояние учебной группы в конкретном учебном семестре.

    semester_number — номер семестра по учебному плану.
    academic_semester — календарный осенний или весенний семестр.
    """

    class Status(models.TextChoices):
        PLANNED = "planned", _("Запланирован")
        ACTIVE = "active", _("Обучение идёт")
        COMPLETED = "completed", _("Завершён")
        CANCELLED = "cancelled", _("Отменён")

    group_curriculum = models.ForeignKey(
        GroupCurriculumAssignment,
        verbose_name=_("Учебный план группы"),
        related_name="group_semesters",
        on_delete=models.PROTECT,
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        verbose_name=_("Учебный год"),
        related_name="group_semesters",
        on_delete=models.PROTECT,
    )
    academic_semester = models.ForeignKey(
        AcademicSemester,
        verbose_name=_("Академический семестр"),
        related_name="group_semesters",
        on_delete=models.PROTECT,
    )
    semester_number = models.PositiveSmallIntegerField(
        _("Номер семестра по учебному плану"),
        validators=[MinValueValidator(1)],
        db_index=True,
    )
    students_count = models.PositiveSmallIntegerField(
        _("Количество студентов в семестре"),
        validators=[MinValueValidator(0)],
    )
    subgroup_count = models.PositiveSmallIntegerField(
        _("Количество подгрупп"),
        default=1,
        validators=[MinValueValidator(1)],
    )
    status = models.CharField(
        _("Статус"),
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
        db_index=True,
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
        verbose_name = _("Семестр учебной группы")
        verbose_name_plural = _("Семестры учебных групп")
        ordering = (
            "-academic_year__start_year",
            "semester_number",
            "group_curriculum__student_group__code",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "group_curriculum",
                    "academic_year",
                    "semester_number",
                ),
                name="unique_group_semester",
            ),
        ]

    @property
    def student_group(self):
        return self.group_curriculum.student_group

    @property
    def curriculum(self):
        return self.group_curriculum.curriculum

    @property
    def season(self):
        return "autumn" if self.semester_number % 2 else "spring"

    def clean(self):
        super().clean()

        if (
            self.academic_semester_id
            and self.academic_year_id
            and self.academic_semester.academic_year_id
            != self.academic_year_id
        ):
            raise ValidationError(
                {
                    "academic_semester": _(
                        "Академический семестр должен относиться "
                        "к выбранному учебному году."
                    )
                }
            )

        if self.academic_semester_id:
            expected_season = (
                AcademicSemester.Season.AUTUMN
                if self.semester_number % 2
                else AcademicSemester.Season.SPRING
            )

            if self.academic_semester.season != expected_season:
                raise ValidationError(
                    {
                        "academic_semester": _(
                            "Нечётный семестр должен быть осенним, "
                            "а чётный — весенним."
                        )
                    }
                )

        if self.group_curriculum_id:
            curriculum = self.group_curriculum.curriculum
            semesters_count = curriculum.semesters_count

            if (
                semesters_count is not None
                and self.semester_number > semesters_count
            ):
                raise ValidationError(
                    {
                        "semester_number": _(
                            "Номер семестра превышает продолжительность "
                            "обучения по учебному плану."
                        )
                    }
                )

    def __str__(self):
        return (
            f"{self.student_group.code}: "
            f"{self.semester_number} семестр, "
            f"{self.academic_year}"
        )

class TeachingStream(BaseModel):
    """
    Учебный поток одного учебного плана
    в конкретном академическом семестре.

    Один поток объединяет учебные группы,
    обучающиеся по одному Curriculum.

    При расчёте нагрузка формируется
    по всем дисциплинам соответствующего
    semester_number и всем их активным
    CurriculumWorkload.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", _("Черновик")
        CALCULATED = "calculated", _("Нагрузка рассчитана")
        APPROVED = "approved", _("Утверждён")
        CANCELLED = "cancelled", _("Отменён")

    academic_year = models.ForeignKey(
        AcademicYear,
        verbose_name=_("Учебный год"),
        related_name="teaching_streams",
        on_delete=models.PROTECT,
    )

    academic_semester = models.ForeignKey(
        AcademicSemester,
        verbose_name=_("Академический семестр"),
        related_name="teaching_streams",
        on_delete=models.PROTECT,
    )

    curriculum = models.ForeignKey(
        Curriculum,
        verbose_name=_("Учебный план"),
        related_name="teaching_streams",
        on_delete=models.PROTECT,
    )

    semester_number = models.PositiveSmallIntegerField(
        _("Номер семестра по учебному плану"),
        validators=[MinValueValidator(1)],
        db_index=True,
    )

    code = models.CharField(
        _("Код потока"),
        max_length=100,
        db_index=True,
    )

    name = models.CharField(
        _("Название потока"),
        max_length=255,
    )

    status = models.CharField(
        _("Статус"),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
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

    group_semesters = models.ManyToManyField(
        GroupSemester,
        verbose_name=_("Учебные группы"),
        related_name="teaching_streams",
        through="TeachingStreamGroup",
    )

    class Meta:
        verbose_name = _("Учебный поток")
        verbose_name_plural = _("Учебные потоки")

        ordering = (
            "-academic_year__start_year",
            "academic_semester__season",
            "curriculum__code",
            "code",
        )

        constraints = [
            models.UniqueConstraint(
                fields=(
                    "academic_year",
                    "academic_semester",
                    "code",
                ),
                name="unique_teaching_stream_code",
            ),
            models.UniqueConstraint(
                fields=(
                    "academic_year",
                    "academic_semester",
                    "curriculum",
                    "semester_number",
                ),
                condition=models.Q(
                    is_active=True,
                    is_archived=False,
                ),
                name="unique_active_curriculum_stream_semester",
            ),
        ]

    @property
    def groups_count(self):
        return self.stream_groups.filter(
            is_archived=False,
            is_active=True,
        ).count()

    @property
    def students_count(self):
        return sum(
            item.group_semester.students_count
            for item in self.stream_groups.filter(
                is_archived=False,
                is_active=True,
            ).select_related("group_semester")
        )

    @property
    def subgroups_count(self):
        return sum(
            item.group_semester.subgroup_count
            for item in self.stream_groups.filter(
                is_archived=False,
                is_active=True,
            ).select_related("group_semester")
        )

    @property
    def season(self):
        return (
            AcademicSemester.Season.AUTUMN
            if self.semester_number % 2
            else AcademicSemester.Season.SPRING
        )

    def clean(self):
        super().clean()

        if (
            self.academic_semester_id
            and self.academic_year_id
            and self.academic_semester.academic_year_id
            != self.academic_year_id
        ):
            raise ValidationError(
                {
                    "academic_semester": _(
                        "Семестр должен относиться "
                        "к выбранному учебному году."
                    )
                }
            )

        if self.academic_semester_id:
            expected_season = (
                AcademicSemester.Season.AUTUMN
                if self.semester_number % 2
                else AcademicSemester.Season.SPRING
            )

            if (
                self.academic_semester.season
                != expected_season
            ):
                raise ValidationError(
                    {
                        "academic_semester": _(
                            "Нечётный семестр учебного плана "
                            "должен быть осенним, "
                            "а чётный — весенним."
                        )
                    }
                )

        if self.curriculum_id:
            semesters_count = (
                self.curriculum.semesters_count
            )

            if (
                semesters_count is not None
                and self.semester_number
                > semesters_count
            ):
                raise ValidationError(
                    {
                        "semester_number": _(
                            "Номер семестра превышает "
                            "продолжительность обучения "
                            "по учебному плану."
                        )
                    }
                )

    def __str__(self):
        return f"{self.code} — {self.name}"

class TeachingStreamGroup(BaseModel):
    """
    Включение группы в учебный поток.
    """

    teaching_stream = models.ForeignKey(
        TeachingStream,
        verbose_name=_("Учебный поток"),
        related_name="stream_groups",
        on_delete=models.CASCADE,
    )
    group_semester = models.ForeignKey(
        GroupSemester,
        verbose_name=_("Семестр учебной группы"),
        related_name="stream_memberships",
        on_delete=models.PROTECT,
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
        verbose_name = _("Группа учебного потока")
        verbose_name_plural = _("Группы учебного потока")
        ordering = (
            "teaching_stream",
            "group_semester__group_curriculum__student_group__code",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "teaching_stream",
                    "group_semester",
                ),
                name="unique_group_in_teaching_stream",
            ),
        ]

    def clean(self):
        super().clean()

        if not self.teaching_stream_id or not self.group_semester_id:
            return

        stream = self.teaching_stream
        group_semester = self.group_semester

        if group_semester.academic_year_id != stream.academic_year_id:
            raise ValidationError(
                {
                    "group_semester": _(
                        "Учебный год группы не совпадает "
                        "с учебным годом потока."
                    )
                }
            )

        if (
                group_semester.academic_semester_id
                != stream.academic_semester_id
        ):
            raise ValidationError(
                {
                    "group_semester": _(
                        "Академический семестр группы не совпадает "
                        "с семестром потока."
                    )
                }
            )

        if (
                group_semester.curriculum.id
                != stream.curriculum_id
        ):
            raise ValidationError(
                {
                    "group_semester": _(
                        "Учебный план группы "
                        "не совпадает с учебным "
                        "планом потока."
                    )
                }
            )

        if (
                group_semester.semester_number
                != stream.semester_number
        ):
            raise ValidationError(
                {
                    "group_semester": _(
                        "Номер семестра группы "
                        "не совпадает с номером "
                        "семестра потока."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.teaching_stream.code}: "
            f"{self.group_semester.student_group.code}"
        )

class PlannedWorkload(BaseModel):
    """
    Рассчитанная плановая нагрузка учебного потока.

    Запись пересчитывается на основании вида нагрузки,
    количества групп, подгрупп или студентов.
    """

    class Status(models.TextChoices):
        CALCULATED = "calculated", _("Рассчитана")
        APPROVED = "approved", _("Утверждена")
        PARTIALLY_DISTRIBUTED = ("partially_distributed", _("Частично распределена"),)
        DISTRIBUTED = "distributed", _("Полностью распределена")
        CANCELLED = "cancelled", _("Отменена")

    teaching_stream = models.ForeignKey(
        TeachingStream,
        verbose_name=_("Учебный поток"),
        related_name="planned_workloads",
        on_delete=models.CASCADE,
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        verbose_name=_("Учебный год"),
        related_name="planned_workloads",
        on_delete=models.PROTECT,
    )
    academic_semester = models.ForeignKey(
        AcademicSemester,
        verbose_name=_("Академический семестр"),
        related_name="planned_workloads",
        on_delete=models.PROTECT,
    )
    teaching_department = models.ForeignKey(
        Department,
        verbose_name=_("Обеспечивающая кафедра"),
        related_name="planned_workloads",
        on_delete=models.PROTECT,
    )
    curriculum_workload = models.ForeignKey(
        CurriculumWorkload,
        verbose_name=_("Вид нагрузки учебного плана"),
        related_name="planned_workloads",
        on_delete=models.PROTECT,
    )
    calculation_mode = models.CharField(
        _("Способ расчёта"),
        max_length=20,
        choices=WorkloadType.CalculationMode.choices,
    )
    base_hours = models.DecimalField(
        _("Базовые часы"),
        max_digits=10,
        decimal_places=2,
    )
    calculation_quantity = models.DecimalField(
        _("Расчётное количество"),
        max_digits=10,
        decimal_places=2,
    )
    total_hours = models.DecimalField(
        _("Итоговые часы"),
        max_digits=12,
        decimal_places=2,
    )
    groups_count = models.PositiveSmallIntegerField(
        _("Количество групп"),
        default=0,
    )
    subgroups_count = models.PositiveSmallIntegerField(
        _("Количество подгрупп"),
        default=0,
    )
    students_count = models.PositiveIntegerField(
        _("Количество студентов"),
        default=0,
    )
    status = models.CharField(
        _("Статус"),
        max_length=30,
        choices=Status.choices,
        default=Status.CALCULATED,
        db_index=True,
    )
    calculated_at = models.DateTimeField(
        _("Дата и время расчёта"),
        auto_now=True,
    )
    notes = models.TextField(
        _("Примечание"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Плановая нагрузка")
        verbose_name_plural = _("Плановая нагрузка")
        ordering = (
            "-academic_year__start_year",
            "teaching_department",
            "teaching_stream__code",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "teaching_stream",
                    "curriculum_workload",
                ),
                name="unique_stream_curriculum_workload",
            ),
        ]

    def __str__(self):
        return (
            f"{self.teaching_stream.code}: "
            f"{self.total_hours} часов"
        )

    @property
    def distributed_hours(self):
        return (
            self.distributions.filter(
                is_archived=False,
                status__in=(
                    "draft",
                    "approved",
                ),
            ).aggregate(
                total=models.Sum("allocated_hours")
            )["total"]
            or Decimal("0.00")
        )

    @property
    def remaining_hours(self):
        remaining = self.total_hours - self.distributed_hours

        if remaining < 0:
            return Decimal("0.00")

        return remaining

    @property
    def distribution_percent(self):
        if not self.total_hours:
            return Decimal("0.00")

        return (
            self.distributed_hours
            / self.total_hours
            * Decimal("100.00")
        ).quantize(Decimal("0.01"))

    @property
    def is_fully_distributed(self):
        return self.remaining_hours == Decimal("0.00")