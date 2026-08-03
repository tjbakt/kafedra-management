from django.test import SimpleTestCase

from apps.workload.api.filters import (
    WorkloadDistributionFilter,
)


class WorkloadDistributionFilterTests(
    SimpleTestCase
):
    def test_declared_filters(self):
        expected = {
            "academic_year",
            "academic_semester",
            "teaching_department",
            "faculty",
            "planned_workload",
            "teaching_stream",
            "discipline",
            "workload_type",
            "staff_member",
            "staff_employment",
            "position",
            "status",
        }

        self.assertEqual(
            set(
                WorkloadDistributionFilter
                .base_filters
            ),
            expected,
        )