from decimal import Decimal

import factory

from apps.curriculum.models import (
    WorkloadType,
)
from apps.teaching.models import (
    GroupCurriculumAssignment,
    GroupSemester,
    PlannedWorkload,
    TeachingStream,
    TeachingStreamGroup,
)
from tests.factories.academics import (
    AcademicSemesterFactory,
    AcademicYearFactory,
    StudentGroupFactory,
)
from tests.factories.curriculum import (
    CurriculumDisciplineFactory,
    CurriculumFactory,
    CurriculumWorkloadFactory,
)


class GroupCurriculumAssignmentFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = GroupCurriculumAssignment

    curriculum = factory.SubFactory(
        CurriculumFactory
    )

    student_group = factory.LazyAttribute(
        lambda obj: StudentGroupFactory(
            study_program=(
                obj.curriculum.study_program
            ),
            study_form=(
                obj.curriculum.study_form
            ),
            faculty=(
                obj.curriculum
                .study_program
                .profiling_department
                .faculty
            ),
            created_by=obj.curriculum.created_by,
            updated_by=obj.curriculum.updated_by,
        )
    )

    start_academic_year = (
        factory.SubFactory(
            AcademicYearFactory
        )
    )
    end_academic_year = None

    is_primary = True
    is_active = True
    notes = ""

    created_by = factory.SelfAttribute(
        "curriculum.created_by"
    )
    updated_by = factory.SelfAttribute(
        "curriculum.updated_by"
    )


class GroupSemesterFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = GroupSemester

    group_curriculum = factory.SubFactory(
        GroupCurriculumAssignmentFactory
    )

    academic_year = factory.SubFactory(
        AcademicYearFactory
    )

    academic_semester = factory.LazyAttribute(
        lambda obj: AcademicSemesterFactory(
            academic_year=obj.academic_year,
            created_by=obj.created_by,
            updated_by=obj.updated_by,
        )
    )

    semester_number = 1
    students_count = 25
    subgroup_count = 1

    status = GroupSemester.Status.PLANNED
    is_active = True
    notes = ""

    created_by = factory.SelfAttribute(
        "group_curriculum.created_by"
    )
    updated_by = factory.SelfAttribute(
        "group_curriculum.updated_by"
    )


class TeachingStreamFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = TeachingStream

    curriculum_discipline = (
        factory.SubFactory(
            CurriculumDisciplineFactory,
            semester_number=1,
        )
    )

    curriculum_workload = (
        factory.SubFactory(
            CurriculumWorkloadFactory,
            curriculum_discipline=(
                factory.SelfAttribute(
                    "..curriculum_discipline"
                )
            ),
        )
    )

    academic_year = factory.SubFactory(
        AcademicYearFactory
    )

    academic_semester = factory.LazyAttribute(
        lambda obj: AcademicSemesterFactory(
            academic_year=obj.academic_year,
            season="autumn",
            created_by=obj.created_by,
            updated_by=obj.updated_by,
        )
    )

    teaching_department = (
        factory.SelfAttribute(
            "curriculum_discipline."
            "teaching_department"
        )
    )

    code = factory.Sequence(
        lambda number: (
            f"STREAM-{number:05d}"
        )
    )
    name = factory.Sequence(
        lambda number: (
            f"Тестовый поток {number}"
        )
    )

    status = TeachingStream.Status.DRAFT
    is_active = True
    notes = ""

    created_by = factory.SelfAttribute(
        "curriculum_discipline.created_by"
    )
    updated_by = factory.SelfAttribute(
        "curriculum_discipline.updated_by"
    )


class TeachingStreamGroupFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = TeachingStreamGroup

    teaching_stream = factory.SubFactory(
        TeachingStreamFactory
    )

    group_semester = factory.LazyAttribute(
        lambda obj: GroupSemesterFactory(
            group_curriculum=(
                GroupCurriculumAssignmentFactory(
                    curriculum=(
                        obj.teaching_stream
                        .curriculum_discipline
                        .curriculum
                    ),
                    created_by=(
                        obj.teaching_stream.created_by
                    ),
                    updated_by=(
                        obj.teaching_stream.updated_by
                    ),
                )
            ),
            academic_year=(
                obj.teaching_stream.academic_year
            ),
            academic_semester=(
                obj.teaching_stream
                .academic_semester
            ),
            semester_number=(
                obj.teaching_stream
                .curriculum_discipline
                .semester_number
            ),
            created_by=(
                obj.teaching_stream.created_by
            ),
            updated_by=(
                obj.teaching_stream.updated_by
            ),
        )
    )

    is_active = True
    notes = ""

    created_by = factory.SelfAttribute(
        "teaching_stream.created_by"
    )
    updated_by = factory.SelfAttribute(
        "teaching_stream.updated_by"
    )


class PlannedWorkloadFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = PlannedWorkload

    teaching_stream = factory.SubFactory(
        TeachingStreamFactory
    )

    academic_year = factory.SelfAttribute(
        "teaching_stream.academic_year"
    )
    academic_semester = factory.SelfAttribute(
        "teaching_stream.academic_semester"
    )
    teaching_department = factory.SelfAttribute(
        "teaching_stream.teaching_department"
    )
    curriculum_workload = factory.SelfAttribute(
        "teaching_stream.curriculum_workload"
    )

    calculation_mode = factory.LazyAttribute(
        lambda obj: (
            obj.curriculum_workload
            .calculation_mode
        )
    )
    base_hours = factory.LazyAttribute(
        lambda obj: (
            obj.curriculum_workload.base_hours
        )
    )

    calculation_quantity = Decimal("1.00")
    total_hours = Decimal("30.00")

    groups_count = 1
    subgroups_count = 1
    students_count = 25

    status = PlannedWorkload.Status.CALCULATED
    notes = ""

    created_by = factory.SelfAttribute(
        "teaching_stream.created_by"
    )
    updated_by = factory.SelfAttribute(
        "teaching_stream.updated_by"
    )