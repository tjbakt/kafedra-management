from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.workload.models import WorkloadDistribution
from apps.workload.services.distribution_service import (
    WorkloadDistributionService,
)
from apps.workload.tests.factories import (
    create_academic_year,
    create_distribution,
    create_employment,
    create_planned_workload,
    create_staff_member,
    create_user,
    create_year_staff_record,
)


class WorkloadDistributionServiceTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.academic_year = create_academic_year()
        self.planned_workload = create_planned_workload(
            academic_year=self.academic_year,
            total_hours=Decimal("100.00"),
        )
        self.department = self.planned_workload.teaching_department

        self.employment = create_employment(
            department=self.department,
        )
        self.second_employment = create_employment(
            department=self.department,
            staff_member=create_staff_member(
                personnel_number="T-SECOND",
                last_name="Петров",
                first_name="Пётр",
            ),
        )

    def test_cannot_distribute_without_year_staff_record(self):
        with self.assertRaises(ValidationError):
            WorkloadDistributionService.create_distribution(
                planned_workload=self.planned_workload,
                staff_employment=self.employment,
                allocated_hours=Decimal("20.00"),
                user=self.user,
            )

    def test_distribution_created_with_year_record(self):
        create_year_staff_record(
            staff_employment=self.employment,
            academic_year=self.academic_year,
        )

        distribution = WorkloadDistributionService.create_distribution(
            planned_workload=self.planned_workload,
            staff_employment=self.employment,
            allocated_hours=Decimal("20.00"),
            user=self.user,
        )

        self.assertEqual(
            distribution.status,
            WorkloadDistribution.Status.DRAFT,
        )
        self.assertEqual(
            distribution.allocated_hours,
            Decimal("20.00"),
        )

    def test_cannot_exceed_remaining_hours(self):
        create_year_staff_record(
            staff_employment=self.employment,
            academic_year=self.academic_year,
        )
        create_year_staff_record(
            staff_employment=self.second_employment,
            academic_year=self.academic_year,
        )

        WorkloadDistributionService.create_distribution(
            planned_workload=self.planned_workload,
            staff_employment=self.employment,
            allocated_hours=Decimal("80.00"),
            user=self.user,
        )

        with self.assertRaises(ValidationError):
            WorkloadDistributionService.create_distribution(
                planned_workload=self.planned_workload,
                staff_employment=self.second_employment,
                allocated_hours=Decimal("30.00"),
                user=self.user,
            )

    def test_approve_sets_correct_status(self):
        create_year_staff_record(
            staff_employment=self.employment,
            academic_year=self.academic_year,
        )

        distribution = WorkloadDistributionService.create_distribution(
            planned_workload=self.planned_workload,
            staff_employment=self.employment,
            allocated_hours=Decimal("20.00"),
            user=self.user,
        )
        distribution = WorkloadDistributionService.approve_distribution(
            distribution=distribution,
            user=self.user,
        )

        self.assertEqual(
            distribution.status,
            WorkloadDistribution.Status.APPROVED,
        )
        self.assertIsNotNone(distribution.approved_at)
        self.assertEqual(distribution.approved_by, self.user)

    def test_approved_distribution_cannot_be_updated(self):
        create_year_staff_record(
            staff_employment=self.employment,
            academic_year=self.academic_year,
        )

        distribution = WorkloadDistributionService.create_distribution(
            planned_workload=self.planned_workload,
            staff_employment=self.employment,
            allocated_hours=Decimal("20.00"),
            user=self.user,
        )
        distribution = WorkloadDistributionService.approve_distribution(
            distribution=distribution,
            user=self.user,
        )

        with self.assertRaises(ValidationError):
            WorkloadDistributionService.update_distribution(
                distribution=distribution,
                allocated_hours=Decimal("25.00"),
                user=self.user,
            )

    def test_cancel_releases_planned_hours(self):
        create_year_staff_record(
            staff_employment=self.employment,
            academic_year=self.academic_year,
        )

        distribution = WorkloadDistributionService.create_distribution(
            planned_workload=self.planned_workload,
            staff_employment=self.employment,
            allocated_hours=Decimal("20.00"),
            user=self.user,
        )
        WorkloadDistributionService.cancel_distribution(
            distribution=distribution,
            user=self.user,
            reason="Перераспределение",
        )

        remaining = WorkloadDistributionService.get_remaining_hours(
            self.planned_workload,
        )
        self.assertEqual(
            remaining,
            self.planned_workload.total_hours,
        )

    def test_draft_and_approved_consume_hours(self):
        create_year_staff_record(
            staff_employment=self.employment,
            academic_year=self.academic_year,
        )
        create_year_staff_record(
            staff_employment=self.second_employment,
            academic_year=self.academic_year,
        )

        d1 = WorkloadDistributionService.create_distribution(
            planned_workload=self.planned_workload,
            staff_employment=self.employment,
            allocated_hours=Decimal("40.00"),
            user=self.user,
        )
        WorkloadDistributionService.approve_distribution(
            distribution=d1,
            user=self.user,
        )
        WorkloadDistributionService.create_distribution(
            planned_workload=self.planned_workload,
            staff_employment=self.second_employment,
            allocated_hours=Decimal("30.00"),
            user=self.user,
        )

        remaining = WorkloadDistributionService.get_remaining_hours(
            self.planned_workload,
        )
        self.assertEqual(remaining, Decimal("30.00"))