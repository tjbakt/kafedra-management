from datetime import date

from django.test import TestCase

from apps.academics.api.serializers import (
    AcademicYearSerializer,
    EducationDurationSerializer,
    ReopenAcademicYearSerializer,
    StudentGroupSerializer,
    StudyProgramSerializer,
)
from apps.academics.models import (
    EducationLevel,
    StudyForm,
)
from tests.factories import (
    AcademicYearFactory,
    DepartmentFactory,
    EducationLevelFactory,
    FacultyFactory,
    StudentGroupFactory,
    StudyFormFactory,
    StudyProgramFactory,
    UniversityFactory,
)


class AcademicYearSerializerTests(TestCase):
    def test_valid_year(self):
        serializer = AcademicYearSerializer(
            data={
                "start_year": 2026,
                "end_year": 2027,
                "is_current": False,
                "is_active": True,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_invalid_year_range(self):
        serializer = AcademicYearSerializer(
            data={
                "start_year": 2026,
                "end_year": 2028,
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "end_year",
            serializer.errors,
        )

    def test_closed_year_cannot_be_edited(self):
        academic_year = (
            AcademicYearFactory.closed()
        )

        serializer = AcademicYearSerializer(
            academic_year,
            data={
                "is_active": True,
            },
            partial=True,
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "academic_year",
            serializer.errors,
        )


class ReopenSerializerTests(TestCase):
    def test_requires_reason(self):
        serializer = ReopenAcademicYearSerializer(
            data={}
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "reason",
            serializer.errors,
        )

    def test_rejects_whitespace(self):
        serializer = ReopenAcademicYearSerializer(
            data={
                "reason": "   ",
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )

    def test_trims_reason(self):
        serializer = ReopenAcademicYearSerializer(
            data={
                "reason": "  Исправление данных  ",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )
        self.assertEqual(
            serializer.validated_data["reason"],
            "Исправление данных",
        )


class EducationDurationSerializerTests(
    TestCase
):
    def test_rejects_inconsistent_duration(self):
        serializer = EducationDurationSerializer(
            data={
                "education_level": (
                    EducationLevelFactory().pk
                ),
                "study_form": (
                    StudyFormFactory().pk
                ),
                "duration_months": 42,
                "semesters_count": 8,
                "is_active": True,
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "duration_months",
            serializer.errors,
        )


class StudyProgramSerializerTests(TestCase):
    def test_code_is_normalized(self):
        department = DepartmentFactory()

        serializer = StudyProgramSerializer(
            data={
                "university": (
                    department
                    .faculty
                    .university_id
                ),
                "education_level": (
                    EducationLevelFactory().pk
                ),
                "code": " 606-test ",
                "name_ru": "Направление",
                "name_uz": "Yo‘nalish",
                "profiling_department": (
                    department.pk
                ),
                "is_active": True,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )
        self.assertEqual(
            serializer.validated_data["code"],
            "606-TEST",
        )

    def test_rejects_department_of_other_university(
        self,
    ):
        university = UniversityFactory()
        department = DepartmentFactory()

        serializer = StudyProgramSerializer(
            data={
                "university": university.pk,
                "education_level": (
                    EducationLevelFactory().pk
                ),
                "code": "60610100",
                "name_ru": "Направление",
                "name_uz": "Yo‘nalish",
                "profiling_department": (
                    department.pk
                ),
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "profiling_department",
            serializer.errors,
        )


class StudentGroupSerializerTests(TestCase):
    def test_code_is_normalized(self):
        group = StudentGroupFactory()

        serializer = StudentGroupSerializer(
            data={
                "academic_year_admission": (
                    group
                    .academic_year_admission_id
                ),
                "faculty": group.faculty_id,
                "study_program": (
                    group.study_program_id
                ),
                "study_form": (
                    group.study_form_id
                ),
                "code": " group-test ",
                "student_count": 20,
                "subgroup_count": 1,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )
        self.assertEqual(
            serializer.validated_data["code"],
            "GROUP-TEST",
        )

    def test_rejects_unconfigured_duration(self):
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
            code=StudyForm.Code.DISTANCE,
            name_ru="Дистанционная",
            name_uz="Masofaviy",
        )

        serializer = StudentGroupSerializer(
            data={
                "academic_year_admission": (
                    AcademicYearFactory().pk
                ),
                "faculty": (
                    FacultyFactory(
                        university=(
                            program.university
                        )
                    ).pk
                ),
                "study_program": program.pk,
                "study_form": study_form.pk,
                "code": "MASTER-01",
                "student_count": 10,
                "subgroup_count": 1,
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "study_form",
            serializer.errors,
        )