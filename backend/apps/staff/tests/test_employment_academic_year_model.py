from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.staff.models import (
    StaffEmploymentAcademicYear,
    WorkloadNorm,
)
from apps.staff.tests.factories import (
    create_academic_year,
    create_degree,
    create_employment,
    create_title,
)


class StaffEmploymentAcademicYearModelTests(
    TestCase
):
    def setUp(self):
        self.academic_year = create_academic_year()
        self.employment = create_employment()
        self.degree = create_degree()
        self.title = create_title()

    def test_str_contains_teacher_year_and_rate(self):
        record = StaffEmploymentAcademicYear.objects.create(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("0.75"),
            academic_degree=self.degree,
            academic_title=self.title,
        )

        value = str(record)

        self.assertIn(
            str(self.academic_year),
            value,
        )
        self.assertIn("0.75", value)

    def test_degree_and_title_flags(self):
        record = StaffEmploymentAcademicYear(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            academic_degree=self.degree,
            academic_title=None,
        )

        self.assertTrue(
            record.has_academic_degree
        )
        self.assertFalse(
            record.has_academic_title
        )

    def test_only_one_record_per_employment_and_year(
        self,
    ):
        StaffEmploymentAcademicYear.objects.create(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                (
                    StaffEmploymentAcademicYear
                    .objects
                    .create(
                        staff_employment=(
                            self.employment
                        ),
                        academic_year=(
                            self.academic_year
                        ),
                        rate=Decimal("0.50"),
                    )
                )

    def test_inactive_degree_is_rejected(self):
        self.degree.is_active = False
        self.degree.save(
            update_fields=("is_active",)
        )

        record = StaffEmploymentAcademicYear(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            academic_degree=self.degree,
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_get_workload_norm_uses_year_snapshot(
        self,
    ):
        record = StaffEmploymentAcademicYear.objects.create(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("0.75"),
            academic_degree=self.degree,
            academic_title=None,
        )

        expected_norm = WorkloadNorm.objects.create(
            academic_year=self.academic_year,
            rate=Decimal("0.75"),
            has_academic_degree=True,
            has_academic_title=False,
            annual_hours=Decimal("600.00"),
            is_active=True,
        )

        result = record.get_workload_norm()

        self.assertEqual(result, expected_norm)