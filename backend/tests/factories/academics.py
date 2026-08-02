from datetime import date

import factory
from django.utils import timezone

from apps.academics.models import (
    AcademicSemester,
    AcademicYear,
    EducationDuration,
    EducationLevel,
    StudentGroup,
    StudyForm,
    StudyProgram,
)
from tests.factories.accounts import UserFactory
from tests.factories.organizations import (
    DepartmentFactory,
)


class AcademicYearFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = AcademicYear

    start_year = factory.Sequence(
        lambda number: 2020 + number
    )
    end_year = factory.LazyAttribute(
        lambda obj: obj.start_year + 1
    )

    is_current = False
    is_active = True
    status = AcademicYear.Status.OPEN

    closed_at = None
    closed_by = None
    closing_comment = ""

    reopened_at = None
    reopened_by = None
    reopening_reason = ""

    created_by = factory.SubFactory(
        UserFactory
    )
    updated_by = factory.SelfAttribute(
        "created_by"
    )

    @classmethod
    def closed(
        cls,
        *,
        user=None,
        **kwargs,
    ):
        user = user or UserFactory()

        return cls(
            status=AcademicYear.Status.CLOSED,
            is_current=False,
            is_active=False,
            closed_at=timezone.now(),
            closed_by=user,
            created_by=user,
            updated_by=user,
            **kwargs,
        )


class EducationLevelFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = EducationLevel
        django_get_or_create = (
            "code",
        )

    code = EducationLevel.Code.BACHELOR
    name_ru = "Бакалавриат"
    name_uz = "Bakalavriat"
    is_active = True
    sort_order = 10

    created_by = factory.SubFactory(
        UserFactory
    )
    updated_by = factory.SelfAttribute(
        "created_by"
    )


class StudyFormFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = StudyForm
        django_get_or_create = (
            "code",
        )

    code = StudyForm.Code.FULL_TIME
    name_ru = "Дневная"
    name_uz = "Kunduzgi"
    is_active = True
    sort_order = 10

    created_by = factory.SubFactory(
        UserFactory
    )
    updated_by = factory.SelfAttribute(
        "created_by"
    )


class EducationDurationFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = EducationDuration

    education_level = factory.SubFactory(
        EducationLevelFactory
    )
    study_form = factory.SubFactory(
        StudyFormFactory
    )

    duration_months = 48
    semesters_count = 8
    is_active = True

    created_by = factory.SelfAttribute(
        "education_level.created_by"
    )
    updated_by = factory.SelfAttribute(
        "education_level.updated_by"
    )


class AcademicSemesterFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = AcademicSemester

    academic_year = factory.SubFactory(
        AcademicYearFactory
    )
    season = AcademicSemester.Season.AUTUMN

    start_date = factory.LazyAttribute(
        lambda obj: date(
            obj.academic_year.start_year,
            9,
            1,
        )
    )
    end_date = factory.LazyAttribute(
        lambda obj: date(
            obj.academic_year.start_year,
            12,
            31,
        )
    )

    is_current = False
    is_active = True

    created_by = factory.SelfAttribute(
        "academic_year.created_by"
    )
    updated_by = factory.SelfAttribute(
        "academic_year.updated_by"
    )

    @classmethod
    def spring(
        cls,
        *,
        academic_year=None,
        **kwargs,
    ):
        academic_year = (
            academic_year
            or AcademicYearFactory()
        )

        return cls(
            academic_year=academic_year,
            season=AcademicSemester.Season.SPRING,
            start_date=date(
                academic_year.end_year,
                2,
                1,
            ),
            end_date=date(
                academic_year.end_year,
                6,
                30,
            ),
            **kwargs,
        )


class StudyProgramFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = StudyProgram

    profiling_department = factory.SubFactory(
        DepartmentFactory
    )

    university = factory.SelfAttribute(
        "profiling_department."
        "faculty.university"
    )

    education_level = factory.SubFactory(
        EducationLevelFactory
    )

    code = factory.Sequence(
        lambda number: f"606-{number:04d}"
    )
    name_ru = factory.Sequence(
        lambda number: (
            f"Тестовое направление {number}"
        )
    )
    name_uz = factory.Sequence(
        lambda number: (
            f"Test yo‘nalishi {number}"
        )
    )

    is_active = True
    sort_order = 0

    created_by = factory.SelfAttribute(
        "profiling_department.created_by"
    )
    updated_by = factory.SelfAttribute(
        "profiling_department.updated_by"
    )


class StudentGroupFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = StudentGroup

    academic_year_admission = factory.SubFactory(
        AcademicYearFactory
    )

    study_program = factory.SubFactory(
        StudyProgramFactory
    )

    faculty = factory.LazyAttribute(
        lambda obj: (
            obj.study_program
            .profiling_department
            .faculty
        )
    )

    study_form = factory.SubFactory(
        StudyFormFactory
    )

    code = factory.Sequence(
        lambda number: f"GROUP-{number:04d}"
    )

    student_count = 25
    subgroup_count = 1
    is_active = True
    graduation_academic_year = None
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

        EducationDuration.objects.get_or_create(
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