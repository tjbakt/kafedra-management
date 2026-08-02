from django.test import SimpleTestCase

from apps.curriculum.api.filters import (
    CurriculumDisciplineFilter,
    CurriculumFilter,
    CurriculumWorkloadFilter,
    DisciplineFilter,
    WorkloadTypeFilter,
)


class CurriculumFilterDeclarationTests(
    SimpleTestCase
):
    def test_discipline_filters(self):
        expected = {
            "query",
            "default_department",
            "faculty",
            "is_active",
        }

        self.assertEqual(
            set(DisciplineFilter.base_filters),
            expected,
        )

    def test_workload_type_filters(self):
        expected = {
            "calculation_mode",
            "is_classroom",
            "is_teaching_load",
            "is_active",
        }

        self.assertEqual(
            set(WorkloadTypeFilter.base_filters),
            expected,
        )

    def test_curriculum_filters(self):
        expected = {
            "query",
            "university",
            "study_program",
            "education_level",
            "study_form",
            "effective_academic_year",
            "status",
            "is_active",
        }

        self.assertEqual(
            set(CurriculumFilter.base_filters),
            expected,
        )

    def test_curriculum_discipline_filters(
        self,
    ):
        expected = {
            "curriculum",
            "discipline",
            "semester_number",
            "season",
            "teaching_department",
            "faculty",
            "control_form",
            "component_type",
            "is_active",
        }

        self.assertEqual(
            set(
                CurriculumDisciplineFilter
                .base_filters
            ),
            expected,
        )

    def test_curriculum_workload_filters(
        self,
    ):
        expected = {
            "curriculum_discipline",
            "curriculum",
            "workload_type",
            "calculation_mode",
            "is_active",
        }

        self.assertEqual(
            set(
                CurriculumWorkloadFilter
                .base_filters
            ),
            expected,
        )