from decimal import Decimal

from django.test import TestCase

from apps.workload.models import (
    WorkloadDistribution,
)
from apps.workload.services.workload_dashboard_service import (
    WorkloadDashboardService,
)
from apps.workload.tests.factories import (
    create_academic_year,
    create_distribution,
    create_employment,
    create_planned_workload,
    create_workload_norm,
    create_year_staff_record,
)


class WorkloadDashboardServiceTests(TestCase):
    def setUp(self):
        self.academic_year = create_academic_year()

        self.planned = create_planned_workload(
            academic_year=self.academic_year,
            total_hours=Decimal("100.00"),
        )
        self.department = (
            self.planned.teaching_department
        )

        self.employment = create_employment(
            department=self.department,
        )

        create_year_staff_record(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
        )

        create_workload_norm(
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            annual_hours=Decimal("600.00"),
        )

    def test_dashboard_calculates_totals(self):
        create_distribution(
            planned_workload=self.planned,
            staff_employment=self.employment,
            allocated_hours=Decimal("25.00"),
            status=(
                WorkloadDistribution.Status.DRAFT
            ),
        )

        # Второй преподаватель — утверждено
        employment2 = create_employment(department=self.department)
        create_year_staff_record(
            staff_employment=employment2,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
        )
        create_distribution(
            planned_workload=self.planned,
            staff_employment=employment2,
            allocated_hours=Decimal("35.00"),
            status=WorkloadDistribution.Status.APPROVED,
        )

        result = (
            WorkloadDashboardService.get_dashboard(
                academic_year=self.academic_year,
                department_id=self.department.id,
            )
        )

        self.assertEqual(
            result["workload"]["planned_positions"],
            1,
        )
        self.assertEqual(
            result["workload"]["planned_hours"],
            Decimal("200.00"),
        )
        self.assertEqual(
            result["workload"]["draft_hours"],
            Decimal("25.00"),
        )
        self.assertEqual(
            result["workload"]["approved_hours"],
            Decimal("35.00"),
        )
        self.assertEqual(
            result["workload"]["distributed_hours"],
            Decimal("60.00"),
        )
        self.assertEqual(
            result["workload"]["remaining_hours"],
            Decimal("140.00"),
        )
        self.assertEqual(
            result["workload"]["distribution_percent"],
            Decimal("30.00"),
        )

        self.assertEqual(
            result["teachers"]["total"],
            2,
        )
        self.assertEqual(
            result["teachers"]["with_norm"],
            2,
        )
        self.assertEqual(
            result["teachers"]["underloaded"],
            2,
        )
        self.assertEqual(
            result["teachers"]["balanced"],
            0,
        )
        self.assertEqual(
            result["teachers"]["overloaded"],
            0,
        )

        self.assertEqual(
            result["departments"]["total"],
            1,
        )
        self.assertEqual(
            result["departments"]["incomplete"],
            1,
        )

    def test_dashboard_respects_empty_access_scope(
        self,
    ):
        result = (
            WorkloadDashboardService.get_dashboard(
                academic_year=self.academic_year,
                allowed_department_ids=set(),
                allowed_staff_member_ids=set(),
            )
        )

        self.assertEqual(
            result["workload"]["planned_positions"],
            0,
        )
        self.assertEqual(
            result["workload"]["planned_hours"],
            Decimal("0.00"),
        )
        self.assertEqual(
            result["teachers"]["total"],
            0,
        )
        self.assertEqual(
            result["departments"]["total"],
            0,
        )

    def test_dashboard_teacher_scope_contains_own_data(
        self,
    ):
        create_distribution(
            planned_workload=self.planned,
            staff_employment=self.employment,
            allocated_hours=Decimal("50.00"),
            status=(
                WorkloadDistribution.Status.DRAFT
            ),
        )

        result = (
            WorkloadDashboardService.get_dashboard(
                academic_year=self.academic_year,
                allowed_department_ids=set(),
                allowed_staff_member_ids={
                    self.employment.staff_member_id,
                },
            )
        )

        self.assertEqual(
            result["teachers"]["total"],
            1,
        )
        self.assertEqual(
            result["teachers"]["distributed_hours"],
            Decimal("50.00"),
        )

        # Преподавателю недоступна агрегированная
        # кафедральная статистика.
        self.assertEqual(
            result["departments"]["total"],
            0,
        )
        self.assertEqual(
            result["workload"]["planned_hours"],
            Decimal("0.00"),
        )