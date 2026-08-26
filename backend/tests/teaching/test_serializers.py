from django.test import TestCase

from apps.teaching.api.serializers import (
    GroupCurriculumAssignmentSerializer,
    GroupSemesterSerializer,
    TeachingStreamGroupSerializer,
    TeachingStreamSerializer,
)
from tests.factories import (
    AcademicSemesterFactory,
    AcademicYearFactory,
    CurriculumDisciplineFactory,
    CurriculumFactory,
    CurriculumWorkloadFactory,
    DepartmentFactory,
    GroupCurriculumAssignmentFactory,
    GroupSemesterFactory,
    StudentGroupFactory,
    TeachingStreamFactory,
)


class GroupCurriculumSerializerTests(
    TestCase
):
    def test_valid_assignment(self):
        curriculum = CurriculumFactory()

        group = StudentGroupFactory(
            study_program=(
                curriculum.study_program
            ),
            study_form=curriculum.study_form,
            faculty=(
                curriculum
                .study_program
                .profiling_department
                .faculty
            ),
        )

        serializer = (
            GroupCurriculumAssignmentSerializer(
                data={
                    "student_group": group.pk,
                    "curriculum": curriculum.pk,
                    "start_academic_year": (
                        AcademicYearFactory().pk
                    ),
                    "is_primary": True,
                    "is_active": True,
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_rejects_earlier_end_year(self):
        source = (
            GroupCurriculumAssignmentFactory()
        )

        serializer = (
            GroupCurriculumAssignmentSerializer(
                data={
                    "student_group": (
                        source.student_group_id
                    ),
                    "curriculum": (
                        source.curriculum_id
                    ),
                    "start_academic_year": (
                        AcademicYearFactory(
                            start_year=2030,
                            end_year=2031,
                        ).pk
                    ),
                    "end_academic_year": (
                        AcademicYearFactory(
                            start_year=2029,
                            end_year=2030,
                        ).pk
                    ),
                }
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "end_academic_year",
            serializer.errors,
        )


class GroupSemesterSerializerTests(
    TestCase
):
    def test_rejects_semester_outside_academic_year(
            self,
    ):
        assignment = (
            GroupCurriculumAssignmentFactory()
        )

        academic_year = (
            assignment
            .start_academic_year
        )

        serializer = (
            GroupSemesterSerializer(
                data={
                    "group_curriculum":
                        assignment.pk,

                    "academic_year":
                        academic_year.pk,

                    "semester_number":
                        3,

                    "weeks_count":
                        15,

                    "students_count":
                        20,

                    "subgroup_count":
                        1,
                }
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "semester_number",
            serializer.errors,
        )


class TeachingStreamSerializerTests(TestCase):
    def test_code_is_normalized(self):
        curriculum = CurriculumFactory()
        year = AcademicYearFactory()
        semester = AcademicSemesterFactory(
            academic_year=year,
        )

        serializer = TeachingStreamSerializer(
            data={
                "academic_year": year.pk,
                "academic_semester": semester.pk,
                "curriculum": curriculum.pk,
                "semester_number": 1,
                "code": " stream-test ",
                "name": "Тестовый поток",
                "is_active": True,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )
        self.assertEqual(
            serializer.validated_data["code"],
            "STREAM-TEST",
        )

    def test_rejects_wrong_academic_year(self):
        curriculum = CurriculumFactory()

        serializer = TeachingStreamSerializer(
            data={
                "academic_year": (
                    AcademicYearFactory().pk
                ),
                "academic_semester": (
                    AcademicSemesterFactory().pk
                ),
                "curriculum": curriculum.pk,
                "semester_number": 1,
                "code": "STREAM-WRONG-YEAR",
                "name": "Поток",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "academic_semester",
            serializer.errors,
        )


class TeachingStreamGroupSerializerTests(
    TestCase
):
    def test_rejects_unrelated_group(self):
        stream = TeachingStreamFactory()
        group_semester = GroupSemesterFactory()

        serializer = (
            TeachingStreamGroupSerializer(
                data={
                    "teaching_stream": stream.pk,
                    "group_semester": (
                        group_semester.pk
                    ),
                    "is_active": True,
                }
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "group_semester",
            serializer.errors,
        )