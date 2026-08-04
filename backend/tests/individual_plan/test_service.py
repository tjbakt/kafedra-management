from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import (
    ValidationError,
)
from django.test import TestCase

from apps.individual_plan.models import (
    IndividualPlan,
    IndividualPlanItem,
    IndividualPlanTeachingWorkload,
)
from apps.individual_plan.services.plan_service import (
    IndividualPlanService,
)
from apps.workload.models import (
    WorkloadDistribution,
)
from tests.factories import (
    IndividualPlanFactory,
    IndividualPlanItemFactory,
    IndividualPlanSectionFactory,
    UserFactory,
    WorkloadDistributionFactory,
)


class IndividualPlanServiceTests(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_create_plan(self):
        source = IndividualPlanFactory()

        source.delete()

        plan, created = (
            IndividualPlanService.create_plan(
                staff_employment=(
                    source.staff_employment
                ),
                academic_year=(
                    source.academic_year
                ),
                user=self.user,
            )
        )

        self.assertTrue(created)
        self.assertEqual(
            plan.status,
            IndividualPlan.Status.DRAFT,
        )

    def test_create_plan_is_idempotent(self):
        existing = IndividualPlanFactory()

        plan, created = (
            IndividualPlanService.create_plan(
                staff_employment=(
                    existing.staff_employment
                ),
                academic_year=(
                    existing.academic_year
                ),
                user=self.user,
            )
        )

        self.assertFalse(created)
        self.assertEqual(plan.pk, existing.pk)

    def test_import_teaching_workload(self):
        plan = IndividualPlanFactory()

        IndividualPlanSectionFactory(
            code=(
                IndividualPlanSectionFactory
                ._meta
                .model
                .Code
                .TEACHING
            )
        )

        distribution = WorkloadDistributionFactory(
            staff_employment=(
                plan.staff_employment
            ),
            planned_workload__academic_year=(
                plan.academic_year
            ),
            status=(
                WorkloadDistribution.Status.APPROVED
            ),
            allocated_hours=Decimal("30.00"),
        )

        result = (
            IndividualPlanService
            .import_teaching_workload(
                plan=plan,
                user=self.user,
            )
        )

        self.assertEqual(
            result["created_count"],
            1,
        )
        self.assertEqual(
            result["total_count"],
            1,
        )

        link = (
            IndividualPlanTeachingWorkload.objects
            .get(
                workload_distribution=distribution
            )
        )

        self.assertEqual(
            link.plan_item.individual_plan,
            plan,
        )
        self.assertEqual(
            link.imported_hours,
            Decimal("30.00"),
        )

    def test_import_updates_existing_item(
        self,
    ):
        plan = IndividualPlanFactory()

        IndividualPlanSectionFactory()

        distribution = WorkloadDistributionFactory(
            staff_employment=(
                plan.staff_employment
            ),
            planned_workload__academic_year=(
                plan.academic_year
            ),
            status=(
                WorkloadDistribution.Status.APPROVED
            ),
            allocated_hours=Decimal("20.00"),
        )

        IndividualPlanService.import_teaching_workload(
            plan=plan,
            user=self.user,
        )

        distribution.allocated_hours = (
            Decimal("25.00")
        )
        distribution.save(
            update_fields=("allocated_hours",)
        )

        result = (
            IndividualPlanService
            .import_teaching_workload(
                plan=plan,
                user=self.user,
            )
        )

        self.assertEqual(
            result["updated_count"],
            1,
        )

        link = (
            IndividualPlanTeachingWorkload.objects
            .get(
                workload_distribution=distribution
            )
        )

        self.assertEqual(
            link.imported_hours,
            Decimal("25.00"),
        )
        self.assertEqual(
            link.plan_item.planned_hours,
            Decimal("25.00"),
        )

    def test_empty_plan_cannot_be_submitted(
        self,
    ):
        plan = IndividualPlanFactory()

        with self.assertRaises(
            ValidationError
        ):
            IndividualPlanService.submit_plan(
                plan=plan,
                user=self.user,
            )

    @patch(
        (
            "apps.individual_plan.services."
            "plan_service.AccessService.users_with_role"
        ),
        return_value=[],
    )
    def test_submit_plan(self, mocked_users):
        plan = IndividualPlanFactory()

        IndividualPlanItemFactory(
            individual_plan=plan
        )

        result = (
            IndividualPlanService.submit_plan(
                plan=plan,
                user=self.user,
            )
        )

        result.refresh_from_db()

        self.assertEqual(
            result.status,
            IndividualPlan.Status.SUBMITTED,
        )
        self.assertIsNotNone(
            result.submitted_at
        )

    def test_approve_plan(self):
        plan = IndividualPlanFactory(
            status=(
                IndividualPlan.Status.SUBMITTED
            )
        )

        result = (
            IndividualPlanService.approve_plan(
                plan=plan,
                user=self.user,
            )
        )

        result.refresh_from_db()

        self.assertEqual(
            result.status,
            IndividualPlan.Status.APPROVED,
        )
        self.assertEqual(
            result.approved_by,
            self.user,
        )

    def test_return_plan(self):
        plan = IndividualPlanFactory(
            status=(
                IndividualPlan.Status.SUBMITTED
            )
        )

        result = (
            IndividualPlanService.return_plan(
                plan=plan,
                reviewer_notes="Исправить план",
                user=self.user,
            )
        )

        result.refresh_from_db()

        self.assertEqual(
            result.status,
            IndividualPlan.Status.RETURNED,
        )
        self.assertEqual(
            result.reviewer_notes,
            "Исправить план",
        )