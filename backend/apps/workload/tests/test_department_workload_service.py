from decimal import Decimal

from django.test import TestCase

from apps.workload.models import WorkloadDistribution
from apps.workload.services.department_workload_service import (
    DepartmentWorkloadService,
)
from apps.workload.tests.factories import (
    create_academic_year,
    create_department,
    create_distribution,
    create_employment,
    create_faculty,
    create_planned_workload,
    create_university,
    create_year_staff_record,
    create_staff_member
)

from apps.teaching.models import PlannedWorkload


class DepartmentWorkloadServiceTests(TestCase):
    def setUp(self):
        self.academic_year = create_academic_year()
        university = create_university()
        faculty = create_faculty(university=university)
        self.department = create_department(
            faculty=faculty,
            name_ru="Кафедра 1",
        )

        self.planned = create_planned_workload(
            academic_year=self.academic_year,
            department=self.department,
            total_hours=Decimal("100.00"),
        )
        self.employment = create_employment(
            department=self.department,
        )
        create_year_staff_record(
            staff_employment=self.employment,
            academic_year=self.academic_year,
        )

    def test_department_summary_basic(self):
        second_employment = create_employment(
            department=self.department,
            staff_member=create_staff_member(personnel_number="T-DEP-2"),
        )
        create_year_staff_record(
            staff_employment=second_employment,
            academic_year=self.academic_year,
        )

        create_distribution(
            planned_workload=self.planned,
            staff_employment=self.employment,
            allocated_hours=Decimal("40.00"),
            status=WorkloadDistribution.Status.DRAFT,
        )
        create_distribution(
            planned_workload=self.planned,  # тот же planned
            staff_employment=second_employment,
            allocated_hours=Decimal("30.00"),
            status=WorkloadDistribution.Status.APPROVED,
        )

        result = DepartmentWorkloadService.get_summary(
            academic_year=self.academic_year,
            department_id=self.department.id,
        )
        row = result[0]

        self.assertEqual(row["planned_hours"], Decimal("200.00"))
        self.assertEqual(row["draft_hours"], Decimal("40.00"))
        self.assertEqual(row["approved_hours"], Decimal("30.00"))
        self.assertEqual(row["distributed_hours"], Decimal("70.00"))
        self.assertEqual(row["remaining_hours"], Decimal("130.00"))
        self.assertEqual(row["distribution_status"], "incomplete")

    def test_department_summary_complete(self):
        create_distribution(
            planned_workload=self.planned,
            staff_employment=self.employment,
            allocated_hours=Decimal("100.00"),
            status=WorkloadDistribution.Status.APPROVED,
        )

        result = DepartmentWorkloadService.get_summary(
            academic_year=self.academic_year,
            department_id=self.department.id,
        )
        self.assertEqual(result[0]["distribution_status"], "complete")
        self.assertEqual(result[0]["remaining_hours"], Decimal("0.00"))

    def test_filter_by_academic_year(self):
        other_year = create_academic_year(
            start_year=2024,
            end_year=2025,
        )
        result = DepartmentWorkloadService.get_summary(
            academic_year=other_year,
            department_id=self.department.id,
        )
        self.assertEqual(result, [])