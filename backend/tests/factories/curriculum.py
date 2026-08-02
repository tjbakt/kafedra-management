from decimal import Decimal

import factory

from apps.curriculum.models import (
    Curriculum,
    CurriculumDiscipline,
    CurriculumWorkload,
    Discipline,
    WorkloadType,
)
from tests.factories.academics import (
    AcademicYearFactory,
    EducationDurationFactory,
    StudyFormFactory,
    StudyProgramFactory,
)
from tests.factories.organizations import (
    DepartmentFactory,
)


class DisciplineFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = Discipline

    code = factory.Sequence(
        lambda number: f"DISC-{number:05d}"
    )
    name_ru = factory.Sequence(
        lambda number: (
            f"Тестовая дисциплина {number}"
        )
    )
    name_uz = factory.Sequence(
        lambda number: (
            f"Test fani {number}"
        )
    )

    default_department = factory.SubFactory(
        DepartmentFactory
    )

    is_active = True
    sort_order = 0

    created_by = factory.SelfAttribute(
        "default_department.created_by"
    )
    updated_by = factory.SelfAttribute(
        "default_department.updated_by"
    )


class WorkloadTypeFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = WorkloadType
        django_get_or_create = (
            "code",
        )

    code = WorkloadType.Code.LECTURE
    name_ru = "Лекции"
    name_uz = "Ma’ruza"

    calculation_mode = (
        WorkloadType.CalculationMode.PER_GROUP
    )
    report_category = (
        WorkloadType.ReportCategory.LECTURE
    )

    is_classroom = True
    is_teaching_load = True
    is_active = True
    sort_order = 10

    created_by = factory.SubFactory(
        "tests.factories.accounts.UserFactory"
    )
    updated_by = factory.SelfAttribute(
        "created_by"
    )


class CurriculumFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = Curriculum

    study_program = factory.SubFactory(
        StudyProgramFactory
    )
    study_form = factory.SubFactory(
        StudyFormFactory
    )
    effective_academic_year = (
        factory.SubFactory(
            AcademicYearFactory
        )
    )

    code = factory.Sequence(
        lambda number: f"CURR-{number:05d}"
    )
    version = 1

    status = Curriculum.Status.DRAFT
    approved_at = None
    approval_document = ""

    is_active = True
    notes = ""

    created_by = factory.SelfAttribute(
        "study_program.created_by"
    )
    updated_by = factory.SelfAttribute(
        "study_program.updated_by"
    )

    @factory.post_generation
    def ensure_duration(
        self,
        create,
        extracted,
        **kwargs,
    ):
        if not create:
            return

        EducationDurationFactory._meta.model.objects.get_or_create(
            education_level=(
                self.study_program.education_level
            ),
            study_form=self.study_form,
            defaults={
                "duration_months": 48,
                "semesters_count": 8,
                "is_active": True,
                "created_by": self.created_by,
                "updated_by": self.updated_by,
            },
        )


class CurriculumDisciplineFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = CurriculumDiscipline

    curriculum = factory.SubFactory(
        CurriculumFactory
    )

    discipline = factory.SubFactory(
        DisciplineFactory
    )

    semester_number = 1

    teaching_department = factory.SelfAttribute(
        "curriculum.study_program."
        "profiling_department"
    )

    component_type = (
        CurriculumDiscipline
        .ComponentType
        .REQUIRED
    )
    control_form = (
        CurriculumDiscipline
        .ControlForm
        .EXAM
    )

    credits = Decimal("6.00")
    total_academic_hours = Decimal("180.00")
    independent_hours = Decimal("90.00")
    weeks_count = 15

    is_active = True
    notes = ""

    created_by = factory.SelfAttribute(
        "curriculum.created_by"
    )
    updated_by = factory.SelfAttribute(
        "curriculum.updated_by"
    )


class CurriculumWorkloadFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = CurriculumWorkload

    curriculum_discipline = (
        factory.SubFactory(
            CurriculumDisciplineFactory
        )
    )

    workload_type = factory.SubFactory(
        WorkloadTypeFactory
    )

    calculation_mode = factory.LazyAttribute(
        lambda obj: (
            obj.workload_type.calculation_mode
        )
    )

    base_hours = Decimal("30.00")
    students_per_unit = None

    is_active = True
    notes = ""

    created_by = factory.SelfAttribute(
        "curriculum_discipline.created_by"
    )
    updated_by = factory.SelfAttribute(
        "curriculum_discipline.updated_by"
    )