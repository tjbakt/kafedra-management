from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.staff.models import (
    StaffEmploymentAcademicYear,
)
from apps.staff.services.academic_year_staff_service import (
    AcademicYearStaffService,
)
from tests.factories import (
    AcademicDegreeFactory,
    AcademicTitleFactory,
    AcademicYearFactory,
    DepartmentFactory,
    StaffEmploymentFactory,
    StaffMemberFactory,
    StaffPositionFactory,
    UserFactory,
)


class AcademicYearStaffServiceTests(
    TestCase
):
    def setUp(self):
        self.user = UserFactory()
        self.year = AcademicYearFactory(
            start_year=2025,
            end_year=2026,
        )
        self.department = DepartmentFactory()

    def create_eligible_employment(
        self,
        **kwargs,
    ):
        return StaffEmploymentFactory(
            department=self.department,
            start_date=date(2020, 9, 1),
            end_date=None,
            is_active=True,
            position=StaffPositionFactory(
                is_teaching_position=True,
            ),
            **kwargs,
        )

    def test_get_eligible_employments(self):
        expected = (
            self.create_eligible_employment()
        )

        StaffEmploymentFactory(
            department=self.department,
            start_date=date(2020, 9, 1),
            is_active=True,
            position=StaffPositionFactory(
                is_teaching_position=False,
            ),
        )

        queryset = (
            AcademicYearStaffService
            .get_eligible_employments(
                academic_year=self.year,
                department=self.department,
            )
        )

        self.assertEqual(
            set(queryset),
            {expected},
        )

    def test_create_missing_records(self):
        degree = AcademicDegreeFactory()
        title = AcademicTitleFactory()

        member = StaffMemberFactory(
            academic_degree=degree,
            academic_title=title,
        )

        employment = (
            self.create_eligible_employment(
                staff_member=member,
                rate=Decimal("0.75"),
            )
        )

        result = (
            AcademicYearStaffService
            .create_missing_records(
                academic_year=self.year,
                department=self.department,
                created_by=self.user,
            )
        )

        self.assertEqual(
            result["created"],
            1,
        )

        record = (
            StaffEmploymentAcademicYear.objects.get(
                staff_employment=employment,
                academic_year=self.year,
            )
        )

        self.assertEqual(
            record.rate,
            Decimal("0.75"),
        )
        self.assertEqual(
            record.academic_degree,
            degree,
        )
        self.assertEqual(
            record.academic_title,
            title,
        )
        self.assertEqual(
            record.created_by,
            self.user,
        )

    def test_existing_record_is_skipped(self):
        employment = (
            self.create_eligible_employment()
        )

        StaffEmploymentAcademicYear.objects.create(
            staff_employment=employment,
            academic_year=self.year,
            rate=employment.rate,
            created_by=self.user,
            updated_by=self.user,
        )

        result = (
            AcademicYearStaffService
            .create_missing_records(
                academic_year=self.year,
                department=self.department,
                created_by=self.user,
            )
        )

        self.assertEqual(
            result["created"],
            0,
        )
        self.assertEqual(
            result["skipped"],
            1,
        )

    def test_archived_record_is_restored(self):
        employment = (
            self.create_eligible_employment()
        )

        record = (
            StaffEmploymentAcademicYear.objects
            .create(
                staff_employment=employment,
                academic_year=self.year,
                rate=employment.rate,
                created_by=self.user,
                updated_by=self.user,
            )
        )
        record.archive(user=self.user)

        result = (
            AcademicYearStaffService
            .create_missing_records(
                academic_year=self.year,
                department=self.department,
                created_by=self.user,
            )
        )

        self.assertEqual(
            result["restored"],
            1,
        )

        record.refresh_from_db()

        self.assertFalse(
            record.is_archived
        )
        self.assertTrue(
            record.is_active
        )

    def test_missing_employments(self):
        missing = (
            self.create_eligible_employment()
        )
        existing = (
            self.create_eligible_employment()
        )

        StaffEmploymentAcademicYear.objects.create(
            staff_employment=existing,
            academic_year=self.year,
            rate=existing.rate,
            created_by=self.user,
            updated_by=self.user,
        )

        queryset = (
            AcademicYearStaffService
            .get_missing_employments(
                academic_year=self.year,
                department=self.department,
            )
        )

        self.assertEqual(
            set(queryset),
            {missing},
        )