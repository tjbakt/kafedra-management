from django.test import SimpleTestCase

from apps.individual_plan.api.filters import (
    IndividualActivityTypeFilter,
    IndividualPlanFilter,
    IndividualPlanItemFilter,
    IndividualPlanSectionFilter,
)


class IndividualPlanFilterTests(
    SimpleTestCase
):
    def test_section_filters(self):
        self.assertEqual(
            set(
                IndividualPlanSectionFilter
                .base_filters
            ),
            {
                "code",
                "is_active",
                "is_hourly",
            },
        )

    def test_activity_filters(self):
        self.assertEqual(
            set(
                IndividualActivityTypeFilter
                .base_filters
            ),
            {
                "section",
                "is_active",
                "requires_evidence",
            },
        )

    def test_plan_filters(self):
        self.assertEqual(
            set(
                IndividualPlanFilter
                .base_filters
            ),
            {
                "academic_year",
                "staff_employment",
                "staff_member",
                "department",
                "faculty",
                "status",
            },
        )

    def test_item_filters(self):
        self.assertEqual(
            set(
                IndividualPlanItemFilter
                .base_filters
            ),
            {
                "individual_plan",
                "academic_year",
                "staff_member",
                "section",
                "activity_type",
                "academic_semester",
                "status",
            },
        )