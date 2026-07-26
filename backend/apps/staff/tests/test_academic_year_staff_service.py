from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.staff.models import (
    StaffEmploymentAcademicYear,
)
from apps.staff.services.academic_year_staff_service import (
    AcademicYearStaffService,
)
from apps.staff.tests.factories import (
    create_academic_year,
    create_degree,
    create_department,
    create_employment,
    create_staff_member,
    create_title,
)


class AcademicYearStaffServiceTests(TestCase):
    def setUp(self):
        self.academic_year = create_academic_year(
            start_year=2026,
            end_year=2027,
        )
        self.department = create_department()

        self.degree = create_degree()
        self.title = create_title()

        self.staff_member = create_staff_member(
            academic_degree=self.degree,
            degree_awarded_date=date(
                2024,
                6,
                15,
            ),
            academic_title=self.title,
            title_awarded_date=date(
                2025,
                2,
                10,
            ),
        )

        self.employment = create_employment(
            staff_member=self.staff_member,
            department=self.department,
            rate=Decimal("0.75"),
        )

    def test_creates_record_from_current_data(self):
        result = (
            AcademicYearStaffService
            .create_missing_records(
                academic_year=self.academic_year,
                department=self.department,
            )
        )

        self.assertEqual(result["created"], 1)

        record = (
            StaffEmploymentAcademicYear
            .objects
            .get(
                staff_employment=self.employment,
                academic_year=self.academic_year,
            )
        )

        self.assertEqual(
            record.rate,
            Decimal("0.75"),
        )
        self.assertEqual(
            record.academic_degree,
            self.degree,
        )
        self.assertEqual(
            record.academic_title,
            self.title,
        )

    def test_second_run_does_not_duplicate_record(
        self,
    ):
        service = AcademicYearStaffService

        service.create_missing_records(
            academic_year=self.academic_year,
            department=self.department,
        )
        result = service.create_missing_records(
            academic_year=self.academic_year,
            department=self.department,
        )

        self.assertEqual(result["created"], 0)
        self.assertEqual(result["skipped"], 1)

        self.assertEqual(
            StaffEmploymentAcademicYear
            .objects
            .filter(
                staff_employment=self.employment,
                academic_year=self.academic_year,
            )
            .count(),
            1,
        )

    def test_existing_rate_is_not_overwritten(self):
        record = (
            StaffEmploymentAcademicYear
            .objects
            .create(
                staff_employment=self.employment,
                academic_year=self.academic_year,
                rate=Decimal("0.50"),
                academic_degree=None,
                academic_title=None,
            )
        )

        (
            AcademicYearStaffService
            .create_missing_records(
                academic_year=self.academic_year,
                department=self.department,
            )
        )

        record.refresh_from_db()

        self.assertEqual(
            record.rate,
            Decimal("0.50"),
        )
        self.assertIsNone(record.academic_degree)
        self.assertIsNone(record.academic_title)

    def test_future_degree_is_not_copied_to_past_year(
        self,
    ):
        past_year = create_academic_year(
            start_year=2023,
            end_year=2024,
            name="2023/2024",
        )

        self.staff_member.degree_awarded_date = date(
            2026,
            5,
            12,
        )
        self.staff_member.save(
            update_fields=(
                "degree_awarded_date",
            )
        )

        (
            AcademicYearStaffService
            .create_missing_records(
                academic_year=past_year,
                department=self.department,
            )
        )

        record = (
            StaffEmploymentAcademicYear
            .objects
            .get(
                staff_employment=self.employment,
                academic_year=past_year,
            )
        )

        self.assertIsNone(record.academic_degree)