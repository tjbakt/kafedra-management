from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.staff.models import (
    StaffEmploymentAcademicYear,
)
from apps.workload.models import WorkloadDistribution
from apps.workload.services.distribution_service import (
    WorkloadDistributionService,
)


class WorkloadDistributionServiceTests(TestCase):
    def test_cannot_distribute_without_year_staff_record(
        self,
    ):
        with self.assertRaises(ValidationError):
            WorkloadDistributionService.create_distribution(
                planned_workload=self.planned_workload,
                staff_employment=self.employment,
                allocated_hours=Decimal("20.00"),
                user=self.user,
            )

    def test_distribution_created_with_year_record(
        self,
    ):
        StaffEmploymentAcademicYear.objects.create(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            created_by=self.user,
            updated_by=self.user,
        )

        distribution = (
            WorkloadDistributionService
            .create_distribution(
                planned_workload=self.planned_workload,
                staff_employment=self.employment,
                allocated_hours=Decimal("20.00"),
                user=self.user,
            )
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
        StaffEmploymentAcademicYear.objects.create(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            created_by=self.user,
            updated_by=self.user,
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
        StaffEmploymentAcademicYear.objects.create(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            created_by=self.user,
            updated_by=self.user,
        )

        distribution = (
            WorkloadDistributionService
            .create_distribution(
                planned_workload=self.planned_workload,
                staff_employment=self.employment,
                allocated_hours=Decimal("20.00"),
                user=self.user,
            )
        )

        distribution = (
            WorkloadDistributionService
            .approve_distribution(
                distribution=distribution,
                user=self.user,
            )
        )

        self.assertEqual(
            distribution.status,
            WorkloadDistribution.Status.APPROVED,
        )
        self.assertIsNotNone(
            distribution.approved_at
        )
        self.assertEqual(
            distribution.approved_by,
            self.user,
        )

    def test_approved_distribution_cannot_be_updated(
        self,
    ):
        StaffEmploymentAcademicYear.objects.create(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            created_by=self.user,
            updated_by=self.user,
        )

        distribution = (
            WorkloadDistributionService
            .create_distribution(
                planned_workload=self.planned_workload,
                staff_employment=self.employment,
                allocated_hours=Decimal("20.00"),
                user=self.user,
            )
        )

        distribution = (
            WorkloadDistributionService
            .approve_distribution(
                distribution=distribution,
                user=self.user,
            )
        )

        with self.assertRaises(ValidationError):
            WorkloadDistributionService.update_distribution(
                distribution=distribution,
                allocated_hours=Decimal("25.00"),
                user=self.user,
            )

    def test_cancel_releases_planned_hours(self):
        StaffEmploymentAcademicYear.objects.create(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            created_by=self.user,
            updated_by=self.user,
        )

        distribution = (
            WorkloadDistributionService
            .create_distribution(
                planned_workload=self.planned_workload,
                staff_employment=self.employment,
                allocated_hours=Decimal("20.00"),
                user=self.user,
            )
        )

        WorkloadDistributionService.cancel_distribution(
            distribution=distribution,
            user=self.user,
            reason="Перераспределение",
        )

        remaining = (
            WorkloadDistributionService
            .get_remaining_hours(
                self.planned_workload
            )
        )

        self.assertEqual(
            remaining,
            self.planned_workload.total_hours,
        )