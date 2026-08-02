from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.staff.models import (
    StaffEmployment,
)
from tests.factories import (
    AcademicDegreeFactory,
    AcademicTitleFactory,
    AcademicYearFactory,
    DepartmentFactory,
    StaffEmploymentAcademicYearFactory,
    StaffEmploymentFactory,
    StaffMemberFactory,
    StaffPositionFactory,
    WorkloadNormFactory,
)


class StaffReferenceModelTests(TestCase):
    def test_position_string(self):
        position = StaffPositionFactory(
            name_ru="Доцент",
        )

        self.assertEqual(
            str(position),
            "Доцент",
        )

    def test_degree_uses_short_name(self):
        degree = AcademicDegreeFactory(
            name_ru="Доктор философии",
            short_name_ru="PhD",
        )

        self.assertEqual(
            str(degree),
            "PhD",
        )

    def test_title_uses_short_name(self):
        title = AcademicTitleFactory(
            name_ru="Доцент",
            short_name_ru="доц.",
        )

        self.assertEqual(
            str(title),
            "доц.",
        )


class StaffMemberModelTests(TestCase):
    def test_full_name(self):
        member = StaffMemberFactory(
            last_name="Иванов",
            first_name="Иван",
            middle_name="Иванович",
        )

        self.assertEqual(
            member.full_name,
            "Иванов Иван Иванович",
        )

    def test_degree_date_requires_degree(self):
        member = StaffMemberFactory.build(
            academic_degree=None,
            degree_awarded_date=date(
                2020,
                1,
                1,
            ),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            member.full_clean()

        self.assertIn(
            "degree_awarded_date",
            context.exception.message_dict,
        )

    def test_title_date_requires_title(self):
        member = StaffMemberFactory.build(
            academic_title=None,
            title_awarded_date=date(
                2020,
                1,
                1,
            ),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            member.full_clean()

        self.assertIn(
            "title_awarded_date",
            context.exception.message_dict,
        )

    def test_birth_date_cannot_be_future(self):
        member = StaffMemberFactory.build(
            birth_date=(
                timezone.localdate()
                + timedelta(days=1)
            ),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            member.full_clean()

        self.assertIn(
            "birth_date",
            context.exception.message_dict,
        )


class StaffEmploymentModelTests(TestCase):
    def test_string_representation(self):
        employment = StaffEmploymentFactory(
            rate=Decimal("0.50"),
        )

        self.assertIn(
            employment.staff_member.full_name,
            str(employment),
        )
        self.assertIn(
            "0.50",
            str(employment),
        )

    def test_end_date_cannot_precede_start(
        self,
    ):
        employment = (
            StaffEmploymentFactory.build(
                start_date=date(2025, 9, 1),
                end_date=date(2025, 8, 31),
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            employment.full_clean()

        self.assertIn(
            "end_date",
            context.exception.message_dict,
        )

    def test_archived_department_is_invalid(
        self,
    ):
        department = DepartmentFactory()
        department.archive()

        employment = (
            StaffEmploymentFactory.build(
                department=department
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            employment.full_clean()

        self.assertIn(
            "department",
            context.exception.message_dict,
        )

    def test_inactive_position_is_invalid(
        self,
    ):
        position = StaffPositionFactory(
            is_active=False,
        )

        employment = (
            StaffEmploymentFactory.build(
                position=position,
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            employment.full_clean()

        self.assertIn(
            "position",
            context.exception.message_dict,
        )

    def test_primary_forces_primary_type(self):
        employment = (
            StaffEmploymentFactory.build(
                is_primary=True,
                employment_type=(
                    StaffEmployment
                    .EmploymentType
                    .HOURLY
                ),
            )
        )

        employment.clean()

        self.assertEqual(
            employment.employment_type,
            (
                StaffEmployment
                .EmploymentType
                .PRIMARY
            ),
        )


class AcademicYearStaffRecordTests(
    TestCase
):
    def test_snapshot_properties(self):
        record = (
            StaffEmploymentAcademicYearFactory(
                academic_degree=(
                    AcademicDegreeFactory()
                ),
                academic_title=(
                    AcademicTitleFactory()
                ),
            )
        )

        self.assertTrue(
            record.has_academic_degree
        )
        self.assertTrue(
            record.has_academic_title
        )

    def test_employment_after_year_is_invalid(
        self,
    ):
        year = AcademicYearFactory(
            start_year=2025,
            end_year=2026,
        )
        employment = StaffEmploymentFactory(
            start_date=date(2027, 1, 1),
        )

        record = (
            StaffEmploymentAcademicYearFactory
            .build(
                staff_employment=employment,
                academic_year=year,
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            record.full_clean()

        self.assertIn(
            "academic_year",
            context.exception.message_dict,
        )

    def test_inactive_degree_is_invalid(self):
        degree = AcademicDegreeFactory(
            is_active=False,
        )

        record = (
            StaffEmploymentAcademicYearFactory(
                academic_degree=degree,
            )
        )

        with self.assertRaises(
                ValidationError
        ) as context:
            record.full_clean()

        self.assertIn(
            "academic_degree",
            context.exception.message_dict,
        )

    def test_matching_norm_is_returned(self):
        year = AcademicYearFactory()
        degree = AcademicDegreeFactory()
        title = AcademicTitleFactory()

        record = (
            StaffEmploymentAcademicYearFactory(
                academic_year=year,
                rate=Decimal("1.00"),
                academic_degree=degree,
                academic_title=title,
            )
        )

        norm = WorkloadNormFactory(
            academic_year=year,
            rate=Decimal("1.00"),
            has_academic_degree=True,
            has_academic_title=True,
            annual_hours=Decimal("800.00"),
        )

        self.assertEqual(
            record.get_workload_norm(),
            norm,
        )
        self.assertEqual(
            record.get_recommended_annual_hours(),
            Decimal("800.00"),
        )

    def test_missing_norm_returns_none(self):
        record = (
            StaffEmploymentAcademicYearFactory()
        )

        self.assertIsNone(
            record.get_workload_norm()
        )
        self.assertIsNone(
            record.get_recommended_annual_hours()
        )