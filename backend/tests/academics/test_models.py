from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.academics.models import (
    AcademicSemester,
    AcademicYear,
    EducationLevel,
    StudyForm,
)
from tests.factories import (
    AcademicSemesterFactory,
    AcademicYearFactory,
    DepartmentFactory,
    EducationDurationFactory,
    EducationLevelFactory,
    FacultyFactory,
    StudentGroupFactory,
    StudyFormFactory,
    StudyProgramFactory,
    UniversityFactory,
    UserFactory,
)


class AcademicYearModelTests(TestCase):
    def test_name_and_string_representation(self):
        academic_year = AcademicYearFactory(
            start_year=2026,
            end_year=2027,
        )

        self.assertEqual(
            academic_year.name,
            "2026/2027",
        )
        self.assertEqual(
            str(academic_year),
            "2026/2027",
        )

    def test_open_properties(self):
        academic_year = AcademicYearFactory()

        self.assertTrue(
            academic_year.is_open
        )
        self.assertFalse(
            academic_year.is_closed
        )

    def test_end_year_must_follow_start_year(self):
        academic_year = AcademicYearFactory.build(
            start_year=2026,
            end_year=2028,
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            academic_year.full_clean()

        self.assertIn(
            "end_year",
            context.exception.message_dict,
        )

    def test_closed_year_cannot_be_current(self):
        academic_year = AcademicYearFactory.build(
            status=AcademicYear.Status.CLOSED,
            is_current=True,
            is_active=False,
            closed_at=timezone.now(),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            academic_year.full_clean()

        self.assertIn(
            "is_current",
            context.exception.message_dict,
        )

    def test_closed_year_cannot_be_active(self):
        academic_year = AcademicYearFactory.build(
            status=AcademicYear.Status.CLOSED,
            is_current=False,
            is_active=True,
            closed_at=timezone.now(),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            academic_year.full_clean()

        self.assertIn(
            "is_active",
            context.exception.message_dict,
        )

    def test_closed_year_requires_closed_at(self):
        academic_year = AcademicYearFactory.build(
            status=AcademicYear.Status.CLOSED,
            is_current=False,
            is_active=False,
            closed_at=None,
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            academic_year.full_clean()

        self.assertIn(
            "closed_at",
            context.exception.message_dict,
        )

    def test_open_year_rejects_closed_at(self):
        academic_year = AcademicYearFactory.build(
            status=AcademicYear.Status.OPEN,
            closed_at=timezone.now(),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            academic_year.full_clean()

        self.assertIn(
            "closed_at",
            context.exception.message_dict,
        )


class EducationReferenceModelTests(TestCase):
    def test_education_level_string(self):
        level = EducationLevelFactory(
            name_ru="Магистратура",
        )

        self.assertEqual(
            str(level),
            "Магистратура",
        )

    def test_study_form_string(self):
        study_form = StudyFormFactory(
            name_ru="Заочная",
        )

        self.assertEqual(
            str(study_form),
            "Заочная",
        )

    def test_duration_matches_semesters(self):
        duration = EducationDurationFactory.build(
            semesters_count=8,
            duration_months=42,
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            duration.full_clean()

        self.assertIn(
            "duration_months",
            context.exception.message_dict,
        )

    def test_duration_string(self):
        duration = EducationDurationFactory(
            semesters_count=8,
            duration_months=48,
        )

        self.assertIn(
            "8 сем.",
            str(duration),
        )


class AcademicSemesterModelTests(TestCase):
    def test_autumn_semester_string(self):
        semester = AcademicSemesterFactory()

        self.assertIn(
            semester.academic_year.name,
            str(semester),
        )
        self.assertIn(
            semester.get_season_display(),
            str(semester),
        )

    def test_end_date_must_be_after_start(self):
        semester = AcademicSemesterFactory.build(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 8, 31),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            semester.full_clean()

        self.assertIn(
            "end_date",
            context.exception.message_dict,
        )

    def test_autumn_starts_in_start_year(self):
        academic_year = AcademicYearFactory(
            start_year=2026,
            end_year=2027,
        )

        semester = AcademicSemesterFactory.build(
            academic_year=academic_year,
            season=(
                AcademicSemester.Season.AUTUMN
            ),
            start_date=date(2027, 9, 1),
            end_date=date(2027, 12, 31),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            semester.full_clean()

        self.assertIn(
            "start_date",
            context.exception.message_dict,
        )

    def test_spring_starts_in_end_year(self):
        academic_year = AcademicYearFactory(
            start_year=2026,
            end_year=2027,
        )

        semester = AcademicSemesterFactory.build(
            academic_year=academic_year,
            season=(
                AcademicSemester.Season.SPRING
            ),
            start_date=date(2026, 2, 1),
            end_date=date(2026, 6, 30),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            semester.full_clean()

        self.assertIn(
            "start_date",
            context.exception.message_dict,
        )


class StudyProgramModelTests(TestCase):
    def test_string_representation(self):
        program = StudyProgramFactory(
            code="60610100",
            name_ru="Программная инженерия",
        )

        self.assertEqual(
            str(program),
            (
                "60610100 — "
                "Программная инженерия"
            ),
        )

    def test_department_must_belong_to_university(
        self,
    ):
        university = UniversityFactory()
        other_department = DepartmentFactory()

        program = StudyProgramFactory.build(
            university=university,
            profiling_department=(
                other_department
            ),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            program.full_clean()

        self.assertIn(
            "profiling_department",
            context.exception.message_dict,
        )

    def test_archived_department_is_invalid(self):
        department = DepartmentFactory()
        department.archive()

        program = StudyProgramFactory.build(
            university=(
                department.faculty.university
            ),
            profiling_department=department,
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            program.full_clean()

        self.assertIn(
            "profiling_department",
            context.exception.message_dict,
        )


class StudentGroupModelTests(TestCase):
    def test_string_representation(self):
        group = StudentGroupFactory(
            code="PI-101",
        )

        self.assertEqual(
            str(group),
            "PI-101",
        )

    def test_faculty_and_program_same_university(
        self,
    ):
        program = StudyProgramFactory()
        other_faculty = FacultyFactory()

        group = StudentGroupFactory.build(
            study_program=program,
            faculty=other_faculty,
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            group.full_clean()

        self.assertIn(
            "faculty",
            context.exception.message_dict,
        )

    def test_requires_education_duration(self):
        program = StudyProgramFactory(
            education_level=(
                EducationLevelFactory(
                    code=(
                        EducationLevel
                        .Code
                        .MASTER
                    ),
                    name_ru="Магистратура",
                    name_uz="Magistratura",
                )
            )
        )

        study_form = StudyFormFactory(
            code=StudyForm.Code.EVENING,
            name_ru="Вечерняя",
            name_uz="Kechki",
        )

        group = StudentGroupFactory.build(
            study_program=program,
            study_form=study_form,
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            group.full_clean()

        self.assertIn(
            "study_form",
            context.exception.message_dict,
        )

    def test_graduation_year_must_be_later(self):
        admission = AcademicYearFactory(
            start_year=2026,
            end_year=2027,
        )
        graduation = AcademicYearFactory(
            start_year=2025,
            end_year=2026,
        )

        group = StudentGroupFactory.build(
            academic_year_admission=admission,
            graduation_academic_year=graduation,
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            group.full_clean()

        self.assertIn(
            "graduation_academic_year",
            context.exception.message_dict,
        )