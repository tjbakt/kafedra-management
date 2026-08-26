from django.test import SimpleTestCase

from apps.workload.api.filters import (
    WorkloadDistributionFilter,
)


class WorkloadDistributionFilterTests(SimpleTestCase):
    def test_declared_filters(self):
        expected = {
            "academic_year",
            "academic_semester",
            "semester_number",
            "teaching_department",
            "faculty",
            "planned_workload",
            "teaching_stream",
            "student_group",
            "discipline",
            "workload_type",
            "curriculum",
            "staff_member",
            "staff_employment",
            "position",
            "status",
        }

        self.assertEqual(
            set(WorkloadDistributionFilter.base_filters),
            expected,
        )