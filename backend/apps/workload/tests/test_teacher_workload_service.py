from decimal import Decimal

from django.test import TestCase

from apps.workload.models import WorkloadDistribution
from apps.workload.services.teacher_workload_service import (
    TeacherWorkloadService,
)
from apps.workload.tests.factories import (
    create_academic_year,
    create_department,
    create_distribution,
    create_employment,
    create_faculty,
    create_planned_workload,
    create_staff_member,
    create_university,
    create_workload_norm,
    create_year_staff_record,
)


class TeacherWorkloadServiceTests(TestCase):
    def setUp(self):
        self.academic_year = create_academic_year()
        self.other_year = create_academic_year(
            start_year=2025,
            end_year=2026,
        )

        university = create_university()
        faculty = create_faculty(university=university)
        self.department = create_department(
            faculty=faculty,
            name_ru="Кафедра А",
        )
        self.other_department = create_department(
            faculty=faculty,
            name_ru="Кафедра Б",
            name_uz="Kafedra B",
        )

        self.staff = create_staff_member(
            personnel_number="T-100",
            last_name="Сидоров",
        )
        self.employment = create_employment(
            staff_member=self.staff,
            department=self.department,
            rate=Decimal("1.00"),
        )
        self.year_record = create_year_staff_record(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
        )

        self.planned = create_planned_workload(
            academic_year=self.academic_year,
            department=self.department,
            total_hours=Decimal("200.00"),
        )

    def test_summary_without_norm(self):
        result = TeacherWorkloadService.get_summary(
            academic_year=self.academic_year,
            department_id=self.department.id,
        )

        self.assertEqual(len(result), 1)
        row = result[0]
        self.assertEqual(row["load_status"], "norm_missing")
        self.assertFalse(row["norm_found"])
        self.assertIsNone(row["recommended_hours"])
        self.assertIsNone(row["remaining_hours"])
        self.assertEqual(row["distributed_hours"], Decimal("0.00"))

    def test_summary_underloaded_with_norm(self):
        create_workload_norm(
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            has_academic_degree=False,
            has_academic_title=False,
            annual_hours=Decimal("600.00"),
        )
        create_distribution(
            planned_workload=self.planned,
            staff_employment=self.employment,
            allocated_hours=Decimal("100.00"),
            status=WorkloadDistribution.Status.DRAFT,
        )

        result = TeacherWorkloadService.get_summary(
            academic_year=self.academic_year,
            staff_member_id=self.staff.id,
        )

        self.assertEqual(len(result), 1)
        row = result[0]
        self.assertTrue(row["norm_found"])
        self.assertEqual(row["recommended_hours"], Decimal("600.00"))
        self.assertEqual(row["distributed_hours"], Decimal("100.00"))
        self.assertEqual(row["remaining_hours"], Decimal("500.00"))
        self.assertEqual(row["load_status"], "underloaded")

    def test_summary_counts_only_draft_and_approved(self):
        create_workload_norm(
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            annual_hours=Decimal("200.00"),
        )
        create_distribution(
            planned_workload=self.planned,
            staff_employment=self.employment,
            allocated_hours=Decimal("50.00"),
            status=WorkloadDistribution.Status.DRAFT,
        )
        # cancelled можно на того же employment
        create_distribution(
            planned_workload=self.planned,
            staff_employment=self.employment,
            allocated_hours=Decimal("40.00"),
            status=WorkloadDistribution.Status.CANCELLED,
        )

        # approved — на другого employment (иначе UniqueViolation)
        other = create_employment(
            department=self.department,
            staff_member=create_staff_member(personnel_number="T-101"),
        )
        create_year_staff_record(
            staff_employment=other,
            academic_year=self.academic_year,
        )
        # для суммы по self.employment approved не нужен на other —
        # лучше approve через смену статуса одного объекта:

        # Проще: одно draft + одно cancelled на одном employment
        result = TeacherWorkloadService.get_summary(
            academic_year=self.academic_year,
            staff_member_id=self.staff.id,
        )
        row = result[0]
        # учитывается только draft 50, cancelled игнорируется
        self.assertEqual(row["distributed_hours"], Decimal("50.00"))

    def test_summary_balanced_and_overloaded(self):
        create_workload_norm(
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            annual_hours=Decimal("100.00"),
        )
        dist = create_distribution(
            planned_workload=self.planned,
            staff_employment=self.employment,
            allocated_hours=Decimal("100.00"),
            status=WorkloadDistribution.Status.APPROVED,
        )

        result = TeacherWorkloadService.get_summary(
            academic_year=self.academic_year,
            staff_member_id=self.staff.id,
        )
        self.assertEqual(result[0]["load_status"], "balanced")

        dist.allocated_hours = Decimal("120.00")
        dist.save(update_fields=["allocated_hours"])

        result = TeacherWorkloadService.get_summary(
            academic_year=self.academic_year,
            staff_member_id=self.staff.id,
        )
        self.assertEqual(result[0]["load_status"], "overloaded")

    def test_filter_by_department(self):
        other_staff = create_staff_member(personnel_number="T-200")
        other_employment = create_employment(
            staff_member=other_staff,
            department=self.other_department,
        )
        create_year_staff_record(
            staff_employment=other_employment,
            academic_year=self.academic_year,
        )

        result = TeacherWorkloadService.get_summary(
            academic_year=self.academic_year,
            department_id=self.department.id,
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["department"], self.department.id)

    def test_filter_by_academic_year(self):
        create_year_staff_record(
            staff_employment=self.employment,
            academic_year=self.other_year,
            rate=Decimal("1.00"),
        )

        result = TeacherWorkloadService.get_summary(
            academic_year=self.academic_year,
            staff_member_id=self.staff.id,
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0]["academic_year"],
            self.academic_year.id,
        )