from django.test import SimpleTestCase

from apps.teaching.api.filters import (
    GroupCurriculumAssignmentFilter,
    GroupSemesterFilter,
    PlannedWorkloadFilter,
    TeachingStreamFilter,
    TeachingStreamGroupFilter,
)


class TeachingFilterDeclarationTests(
    SimpleTestCase
):
    def test_group_curriculum_filters(self):
        self.assertEqual(
            set(
                GroupCurriculumAssignmentFilter
                .base_filters
            ),
            {
                "student_group",
                "curriculum",
                "start_academic_year",
                "is_primary",
                "is_active",
            },
        )

    def test_group_semester_filters(self):
        expected = {
            "student_group",
            "curriculum",
            "academic_year",
            "academic_semester",
            "semester_number",
            "faculty",
            "profiling_department",
            "status",
            "is_active",
        }

        self.assertEqual(
            set(
                GroupSemesterFilter.base_filters
            ),
            expected,
        )

    def test_stream_filters(self):
        expected = {
            "academic_year",
            "academic_semester",
            "curriculum",
            "semester_number",
            "study_program",
            "study_form",
            "student_group",
            "status",
            "is_active",
        }

        self.assertEqual(
            set(TeachingStreamFilter.base_filters),
            expected,
        )

    def test_planned_workload_filters(self):
        expected = {
            "academic_year",
            "academic_semester",
            "teaching_department",
            "discipline",
            "workload_type",
            "status",
            "is_fully_distributed",
            "curriculum",
            "teaching_stream",
        }

        self.assertEqual(
            set(PlannedWorkloadFilter.base_filters),
            expected,
        )