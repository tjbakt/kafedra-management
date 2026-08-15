from decimal import Decimal

from django.core.exceptions import (
    ValidationError,
)
from django.test import TestCase

from apps.academics.models import (
    AcademicSemester,
)
from apps.curriculum.models import (
    WorkloadType,
)
from apps.teaching.models import (
    GroupCurriculumAssignment,
    GroupSemester,
    TeachingStream
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
    PlannedWorkloadFactory,
    StudentGroupFactory,
    TeachingStreamFactory,
    TeachingStreamGroupFactory,
    WorkloadTypeFactory,
)


class GroupCurriculumAssignmentModelTests(
    TestCase
):
    def test_string_representation(self):
        assignment = (
            GroupCurriculumAssignmentFactory()
        )

        self.assertEqual(
            str(assignment),
            (
                f"{assignment.student_group} — "
                f"{assignment.curriculum.code}"
            ),
        )

    def test_rejects_other_study_program(self):
        student_group = StudentGroupFactory()
        curriculum = CurriculumFactory()

        assignment = (
            GroupCurriculumAssignment(
                student_group=student_group,
                curriculum=curriculum,
                start_academic_year=(
                    AcademicYearFactory()
                ),
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            assignment.full_clean()

        self.assertIn(
            "curriculum",
            context.exception.message_dict,
        )

    def test_end_year_cannot_be_earlier(self):
        curriculum = CurriculumFactory()

        assignment = (
            GroupCurriculumAssignmentFactory(
                curriculum=curriculum,
                start_academic_year=(
                    AcademicYearFactory(
                        start_year=2030,
                        end_year=2031,
                    )
                ),
                end_academic_year=(
                    AcademicYearFactory(
                        start_year=2029,
                        end_year=2030,
                    )
                ),
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            assignment.full_clean()

        self.assertIn(
            "end_academic_year",
            context.exception.message_dict,
        )


class GroupSemesterModelTests(TestCase):
    def test_season_properties(self):
        autumn = GroupSemesterFactory(
            semester_number=1,
        )
        spring = GroupSemesterFactory(
            academic_semester=(
                AcademicSemesterFactory.spring()
            ),
            academic_year=(
                AcademicSemesterFactory
                .spring()
                .academic_year
            ),
            semester_number=2,
        )

        self.assertEqual(
            autumn.season,
            "autumn",
        )
        self.assertEqual(
            spring.season,
            "spring",
        )

    def test_semester_year_must_match(self):
        group_curriculum = (
            GroupCurriculumAssignmentFactory()
        )
        academic_year = AcademicYearFactory()
        other_semester = AcademicSemesterFactory()

        instance = GroupSemester(
            group_curriculum=group_curriculum,
            academic_year=academic_year,
            academic_semester=other_semester,
            semester_number=1,
            students_count=20,
            subgroup_count=1,
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            instance.full_clean()

        self.assertIn(
            "academic_semester",
            context.exception.message_dict,
        )

    def test_odd_semester_requires_autumn(self):
        academic_year = AcademicYearFactory()
        spring = AcademicSemesterFactory.spring(
            academic_year=academic_year,
        )

        instance = GroupSemester(
            group_curriculum=(
                GroupCurriculumAssignmentFactory()
            ),
            academic_year=academic_year,
            academic_semester=spring,
            semester_number=1,
            students_count=20,
            subgroup_count=1,
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            instance.full_clean()

        self.assertIn(
            "academic_semester",
            context.exception.message_dict,
        )


class TeachingStreamModelTests(TestCase):
    def test_counts_active_groups(self):
        stream = TeachingStreamFactory()

        first = TeachingStreamGroupFactory(
            teaching_stream=stream,
        )
        second = TeachingStreamGroupFactory(
            teaching_stream=stream,
        )

        second.group_semester.students_count = 15
        second.group_semester.subgroup_count = 2
        second.group_semester.save(
            update_fields=(
                "students_count",
                "subgroup_count",
            )
        )

        self.assertEqual(stream.groups_count, 2)
        self.assertEqual(
            stream.students_count,
            first.group_semester.students_count + 15,
        )
        self.assertEqual(
            stream.subgroups_count,
            first.group_semester.subgroup_count + 2,
        )

    def test_odd_semester_requires_autumn(self):
        academic_year = AcademicYearFactory()
        spring = AcademicSemesterFactory.spring(
            academic_year=academic_year,
        )

        stream = TeachingStreamFactory.build(
            academic_year=academic_year,
            academic_semester=spring,
            semester_number=1,
            curriculum=CurriculumFactory(),
        )

        with self.assertRaises(ValidationError) as ctx:
            stream.full_clean()

        self.assertIn(
            "academic_semester",
            ctx.exception.message_dict,
        )

    def test_semester_cannot_exceed_duration(self):
        from apps.teaching.models import TeachingStream

        curriculum = CurriculumFactory()
        academic_year = AcademicYearFactory()
        academic_semester = AcademicSemesterFactory(
            academic_year=academic_year,
            season="autumn",
        )

        stream = TeachingStream(
            curriculum=curriculum,
            academic_year=academic_year,
            academic_semester=academic_semester,
            semester_number=99,
            code="STREAM-OVER",
            name="Переполнение",
        )

        with self.assertRaises(ValidationError) as ctx:
            stream.full_clean()

        self.assertIn(
            "semester_number",
            ctx.exception.message_dict,
        )


class TeachingStreamGroupModelTests(
    TestCase
):
    def test_valid_membership(self):
        membership = (
            TeachingStreamGroupFactory()
        )

        membership.full_clean()

    def test_rejects_other_semester(self):
        stream = TeachingStreamFactory()
        group_semester = GroupSemesterFactory()

        membership = TeachingStreamGroupFactory.build(
            teaching_stream=stream,
            group_semester=group_semester,
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            membership.full_clean()

        self.assertIn(
            "group_semester",
            context.exception.message_dict,
        )


class PlannedWorkloadModelTests(TestCase):
    def test_string_representation(self):
        workload = PlannedWorkloadFactory(
            total_hours=Decimal("45.00"),
        )

        self.assertIn(
            workload.teaching_stream.code,
            str(workload),
        )
        self.assertIn(
            "45.00",
            str(workload),
        )

    def test_empty_distribution_properties(self):
        workload = PlannedWorkloadFactory(
            total_hours=Decimal("30.00"),
        )

        self.assertEqual(
            workload.distributed_hours,
            Decimal("0.00"),
        )
        self.assertEqual(
            workload.remaining_hours,
            Decimal("30.00"),
        )
        self.assertEqual(
            workload.distribution_percent,
            Decimal("0.00"),
        )
        self.assertFalse(
            workload.is_fully_distributed
        )