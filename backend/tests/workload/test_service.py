from decimal import Decimal

from django.core.exceptions import (
    ValidationError,
)
from django.test import TestCase

from apps.workload.models import (
    WorkloadDistribution,
)
from apps.workload.services.distribution_service import (
    WorkloadDistributionService,
)
from tests.factories import (
    StaffEmploymentAcademicYearFactory,
    StaffEmploymentFactory,
    UserFactory,
    WorkloadDistributionFactory,
)


class WorkloadDistributionServiceTests(
    TestCase
):
    def setUp(self):
        self.user = UserFactory()

    def test_approve_distribution(self):
        distribution = (
            WorkloadDistributionFactory()
        )

        result = (
            WorkloadDistributionService
            .approve_distribution(
                distribution=distribution,
                user=self.user,
            )
        )

        result.refresh_from_db()

        self.assertEqual(
            result.status,
            WorkloadDistribution.Status.APPROVED,
        )
        self.assertEqual(
            result.approved_by,
            self.user,
        )
        self.assertIsNotNone(
            result.approved_at,
        )

    def test_approve_twice_rejected(self):
        distribution = (
            WorkloadDistributionFactory()
        )

        (
            WorkloadDistributionService
            .approve_distribution(
                distribution=distribution,
                user=self.user,
            )
        )

        with self.assertRaises(
            ValidationError
        ):
            (
                WorkloadDistributionService
                .approve_distribution(
                    distribution=distribution,
                    user=self.user,
                )
            )

    def test_cancel_distribution(self):
        distribution = (
            WorkloadDistributionFactory()
        )

        result = (
            WorkloadDistributionService
            .cancel_distribution(
                distribution=distribution,
                user=self.user,
                reason="Исправление назначения",
            )
        )

        result.refresh_from_db()

        self.assertEqual(
            result.status,
            WorkloadDistribution.Status.CANCELLED,
        )
        self.assertIn(
            "Исправление назначения",
            result.notes,
        )

    def test_restore_cancelled_distribution(
        self,
    ):
        distribution = (
            WorkloadDistributionFactory(
                status=(
                    WorkloadDistribution
                    .Status
                    .CANCELLED
                ),
            )
        )

        result = (
            WorkloadDistributionService
            .restore_distribution(
                distribution=distribution,
                user=self.user,
                reason="Восстановление",
            )
        )

        result.refresh_from_db()

        self.assertEqual(
            result.status,
            WorkloadDistribution.Status.DRAFT,
        )

    def test_return_approved_to_draft(self):
        distribution = (
            WorkloadDistributionFactory()
        )

        distribution = (
            WorkloadDistributionService
            .approve_distribution(
                distribution=distribution,
                user=self.user,
            )
        )

        distribution = (
            WorkloadDistributionService
            .return_distribution_to_draft(
                distribution=distribution,
                user=self.user,
                reason="Корректировка",
            )
        )

        distribution.refresh_from_db()

        self.assertEqual(
            distribution.status,
            WorkloadDistribution.Status.DRAFT,
        )
        self.assertIsNone(
            distribution.approved_at,
        )
        self.assertIsNone(
            distribution.approved_by,
        )

    def test_available_actions_for_draft(self):
        distribution = (
            WorkloadDistributionFactory()
        )

        result = (
            WorkloadDistributionService
            .get_available_actions(
                distribution=distribution
            )
        )

        self.assertEqual(
            result["distribution_id"],
            distribution.pk,
        )
        self.assertEqual(
            result["status"],
            WorkloadDistribution.Status.DRAFT,
        )

        actions = result["actions"]

        self.assertTrue(
            actions["approve"]["allowed"]
        )
        self.assertTrue(
            actions["cancel"]["allowed"]
        )
        self.assertTrue(
            actions["transfer"]["allowed"]
        )
        self.assertTrue(
            actions["edit"]["allowed"]
        )

        self.assertFalse(
            actions["restore"]["allowed"]
        )
        self.assertFalse(
            actions["return_to_draft"]["allowed"]
        )

    def test_transfer_part_of_hours(self):
        source = WorkloadDistributionFactory(
            allocated_hours=Decimal("30.00"),
        )

        target = StaffEmploymentFactory(
            department=(
                source.planned_workload
                .teaching_department
            ),
        )

        StaffEmploymentAcademicYearFactory(
            staff_employment=target,
            academic_year=(
                source.planned_workload
                .academic_year
            ),
        )

        result = (
            WorkloadDistributionService
            .transfer_distribution_hours(
                source_distribution=source,
                target_staff_employment=target,
                transfer_hours=Decimal("10.00"),
                user=self.user,
                reason="Перераспределение",
            )
        )

        source.refresh_from_db()

        self.assertEqual(
            source.allocated_hours,
            Decimal("20.00"),
        )
        self.assertEqual(
            result["target_distribution"]
            .allocated_hours,
            Decimal("10.00"),
        )
        self.assertFalse(
            result["source_cancelled"],
        )

    def test_transfer_all_hours_cancels_source(
        self,
    ):
        source = WorkloadDistributionFactory(
            allocated_hours=Decimal("30.00"),
        )

        target = StaffEmploymentFactory(
            department=(
                source.planned_workload
                .teaching_department
            ),
        )

        StaffEmploymentAcademicYearFactory(
            staff_employment=target,
            academic_year=(
                source.planned_workload
                .academic_year
            ),
        )

        result = (
            WorkloadDistributionService
            .transfer_distribution_hours(
                source_distribution=source,
                target_staff_employment=target,
                transfer_hours=Decimal("30.00"),
                user=self.user,
                reason="Полный перенос",
            )
        )

        source.refresh_from_db()

        self.assertEqual(
            source.status,
            WorkloadDistribution.Status.CANCELLED,
        )
        self.assertTrue(
            result["source_cancelled"],
        )