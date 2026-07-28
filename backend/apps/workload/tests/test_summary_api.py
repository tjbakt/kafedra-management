from decimal import Decimal
from unittest.mock import patch

from io import BytesIO

from openpyxl import load_workbook

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.workload.models import WorkloadDistribution
from apps.workload.tests.factories import (
    create_academic_year,
    create_distribution,
    create_employment,
    create_planned_workload,
    create_user,
    create_workload_norm,
    create_year_staff_record,
)


class WorkloadSummaryApiTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="api-user")
        self.client.force_authenticate(user=self.user)

        self.academic_year = create_academic_year()
        self.planned = create_planned_workload(
            academic_year=self.academic_year,
            total_hours=Decimal("100.00"),
        )
        self.department = self.planned.teaching_department
        self.employment = create_employment(
            department=self.department,
        )
        create_year_staff_record(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
        )

        self.teacher_url = reverse(
            "workload-distribution-teacher-summary"
        )
        self.department_url = reverse(
            "workload-distribution-department-summary"
        )

    def test_teacher_summary_requires_academic_year(self):
        response = self.client.get(self.teacher_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_teacher_summary_ok(self):
        create_workload_norm(
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            annual_hours=Decimal("600.00"),
        )
        create_distribution(
            planned_workload=self.planned,
            staff_employment=self.employment,
            allocated_hours=Decimal("50.00"),
            status=WorkloadDistribution.Status.DRAFT,
        )

        response = self.client.get(
            self.teacher_url,
            {
                "academic_year": self.academic_year.id,
                "department": self.department.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
        row = response.data[0]
        self.assertIn("load_status", row)
        self.assertIn("remaining_hours", row)
        self.assertIn("staff_employment_academic_year", row)

    def test_teacher_summary_filter_department(self):
        response = self.client.get(
            self.teacher_url,
            {
                "academic_year": self.academic_year.id,
                "department": self.department.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for row in response.data:
            self.assertEqual(row["department"], self.department.id)

    def test_department_summary_ok(self):
        create_distribution(
            planned_workload=self.planned,
            staff_employment=self.employment,
            allocated_hours=Decimal("25.00"),
            status=WorkloadDistribution.Status.APPROVED,
        )

        response = self.client.get(
            self.department_url,
            {
                "academic_year": self.academic_year.id,
                "department": self.department.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        # API может вернуть list или dict — поддержи оба варианта
        if isinstance(data, list):
            self.assertGreaterEqual(len(data), 1)
            row = data[0]
        else:
            row = data

        self.assertIn("planned_hours", row)
        self.assertIn("distributed_hours", row)
        self.assertIn("remaining_hours", row)

    def test_department_summary_export_requires_academic_year(
            self,
    ):
        response = self.client.get(
            (
                "/api/v1/workload/distributions/"
                "department-summary/export/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "academic_year",
            response.data,
        )

    def test_department_summary_export_returns_xlsx(self):
        response = self.client.get(
            (
                "/api/v1/workload/distributions/"
                "department-summary/export/"
                f"?academic_year={self.academic_year.id}"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response["Content-Type"],
            (
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        )
        self.assertIn(
            "attachment;",
            response["Content-Disposition"],
        )
        self.assertIn(
            ".xlsx",
            response["Content-Disposition"],
        )

        # XLSX-файл является ZIP-архивом и начинается с PK.
        self.assertTrue(
            response.content.startswith(b"PK")
        )

    def test_department_summary_export_contains_headers(self):
        response = self.client.get(
            (
                "/api/v1/workload/distributions/"
                "department-summary/export/"
                f"?academic_year={self.academic_year.id}"
            )
        )

        workbook = load_workbook(
            filename=BytesIO(response.content),
            read_only=True,
        )
        worksheet = workbook.active

        self.assertEqual(
            worksheet["A3"].value,
            "Кафедра",
        )
        self.assertEqual(
            worksheet["C3"].value,
            "Плановые часы",
        )
        self.assertEqual(
            worksheet["I3"].value,
            "Статус",
        )

        workbook.close()