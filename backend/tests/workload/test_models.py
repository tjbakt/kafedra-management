from decimal import Decimal

from django.core.exceptions import (
    ValidationError,
)
from django.test import TestCase

from apps.workload.models import (
    WorkloadDistribution,
)
from tests.factories import (
    DepartmentFactory,
    PlannedWorkloadFactory,
    StaffEmploymentAcademicYearFactory,
    StaffEmploymentFactory,
    StaffPositionFactory,
    WorkloadDistributionFactory,
)


class WorkloadDistributionModelTests(
    TestCase
):
    def test_string_representation(self):
        distribution = (
            WorkloadDistributionFactory(
                allocated_hours=Decimal("25.00"),
            )
        )

        value = str(distribution)

        self.assertIn(
            distribution.teacher_name,
            value,
        )
        self.assertIn(
            "25.00",
            value,
        )

    def test_properties(self):
        distribution = (
            WorkloadDistributionFactory()
        )

        self.assertEqual(
            distribution.staff_member,
            (
                distribution.staff_employment
                .staff_member
            ),
        )
        self.assertEqual(
            distribution.academic_year,
            (
                distribution.planned_workload
                .academic_year
            ),
        )
        self.assertEqual(
            distribution.teaching_department,
            (
                distribution.planned_workload
                .teaching_department
            ),
        )

    def test_hours_must_be_positive(self):
        planned = PlannedWorkloadFactory()

        employment = StaffEmploymentFactory(
            department=planned.teaching_department,
        )

        StaffEmploymentAcademicYearFactory(
            staff_employment=employment,
            academic_year=planned.academic_year,
        )

        distribution = WorkloadDistribution(
            planned_workload=planned,
            staff_employment=employment,
            allocated_hours=Decimal("0.00"),
        )

        with self.assertRaises(
                ValidationError
        ) as context:
            distribution.full_clean()

        self.assertIn(
            "allocated_hours",
            context.exception.message_dict,
        )

    def test_archived_employment_is_invalid(
        self,
    ):
        planned = PlannedWorkloadFactory()

        employment = StaffEmploymentFactory(
            department=(
                planned.teaching_department
            ),
        )
        employment.archive()

        distribution = (
            WorkloadDistribution(
                planned_workload=planned,
                staff_employment=employment,
                allocated_hours=Decimal("10.00"),
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            distribution.full_clean()

        self.assertIn(
            "staff_employment",
            context.exception.message_dict,
        )

    def test_inactive_employment_is_invalid(
        self,
    ):
        planned = PlannedWorkloadFactory()

        employment = StaffEmploymentFactory(
            department=(
                planned.teaching_department
            ),
            is_active=False,
        )

        distribution = (
            WorkloadDistribution(
                planned_workload=planned,
                staff_employment=employment,
                allocated_hours=Decimal("10.00"),
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            distribution.full_clean()

        self.assertIn(
            "staff_employment",
            context.exception.message_dict,
        )

    def test_non_teaching_position_is_invalid(
        self,
    ):
        planned = PlannedWorkloadFactory()

        employment = StaffEmploymentFactory(
            department=(
                planned.teaching_department
            ),
            position=StaffPositionFactory(
                is_teaching_position=False,
            ),
        )

        distribution = (
            WorkloadDistribution(
                planned_workload=planned,
                staff_employment=employment,
                allocated_hours=Decimal("10.00"),
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            distribution.full_clean()

        self.assertIn(
            "staff_employment",
            context.exception.message_dict,
        )

    def test_department_must_match(self):
        planned = PlannedWorkloadFactory()

        employment = StaffEmploymentFactory(
            department=DepartmentFactory(),
        )

        distribution = (
            WorkloadDistribution(
                planned_workload=planned,
                staff_employment=employment,
                allocated_hours=Decimal("10.00"),
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            distribution.full_clean()

        self.assertIn(
            "staff_employment",
            context.exception.message_dict,
        )

    def test_academic_year_record_required(
        self,
    ):
        planned = PlannedWorkloadFactory()

        employment = StaffEmploymentFactory(
            department=(
                planned.teaching_department
            ),
        )

        distribution = (
            WorkloadDistribution(
                planned_workload=planned,
                staff_employment=employment,
                allocated_hours=Decimal("10.00"),
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            distribution.full_clean()

        self.assertIn(
            "staff_employment",
            context.exception.message_dict,
        )

    def test_over_distribution_is_invalid(self):
        planned = PlannedWorkloadFactory(
            total_hours=Decimal("100.00"),
        )

        first = WorkloadDistributionFactory(
            planned_workload=planned,
            allocated_hours=Decimal("80.00"),
        )

        second_employment = (
            StaffEmploymentFactory(
                department=(
                    planned.teaching_department
                ),
            )
        )

        StaffEmploymentAcademicYearFactory(
            staff_employment=second_employment,
            academic_year=planned.academic_year,
        )

        second = WorkloadDistribution(
            planned_workload=planned,
            staff_employment=second_employment,
            allocated_hours=Decimal("30.00"),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            second.full_clean()

        self.assertIn(
            "allocated_hours",
            context.exception.message_dict,
        )

        first.refresh_from_db()

    def test_exact_remaining_hours_allowed(self):
        planned = PlannedWorkloadFactory(
            total_hours=Decimal("100.00"),
        )

        WorkloadDistributionFactory(
            planned_workload=planned,
            allocated_hours=Decimal("70.00"),
        )

        employment = StaffEmploymentFactory(
            department=(
                planned.teaching_department
            ),
        )

        StaffEmploymentAcademicYearFactory(
            staff_employment=employment,
            academic_year=planned.academic_year,
        )

        distribution = WorkloadDistribution(
            planned_workload=planned,
            staff_employment=employment,
            allocated_hours=Decimal("30.00"),
        )

        distribution.full_clean()