from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.staff.api.serializers import (
    StaffEmploymentAcademicYearSerializer,
    StaffEmploymentSerializer,
    StaffMemberSerializer,
    StaffPositionSerializer,
    WorkloadNormSerializer,
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
)


class StaffPositionSerializerTests(
    TestCase
):
    def test_code_is_normalized(self):
        serializer = StaffPositionSerializer(
            data={
                "code": "  docent ",
                "name_ru": "Доцент",
                "name_uz": "Dotsent",
                "category": "teaching",
                "is_teaching_position": True,
                "is_active": True,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )
        self.assertEqual(
            serializer.validated_data["code"],
            "DOCENT",
        )


class StaffMemberSerializerTests(
    TestCase
):
    def test_personnel_number_normalized(self):
        serializer = StaffMemberSerializer(
            data={
                "personnel_number": " staff-001 ",
                "last_name": "Иванов",
                "first_name": "Иван",
                "middle_name": "",
                "gender": "",
                "is_active": True,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )
        self.assertEqual(
            serializer.validated_data[
                "personnel_number"
            ],
            "STAFF-001",
        )

    def test_degree_date_requires_degree(self):
        serializer = StaffMemberSerializer(
            data={
                "personnel_number": "STAFF-002",
                "last_name": "Иванов",
                "first_name": "Иван",
                "degree_awarded_date": (
                    "2020-01-01"
                ),
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "degree_awarded_date",
            serializer.errors,
        )

    def test_title_date_requires_title(self):
        serializer = StaffMemberSerializer(
            data={
                "personnel_number": "STAFF-003",
                "last_name": "Иванов",
                "first_name": "Иван",
                "title_awarded_date": (
                    "2020-01-01"
                ),
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "title_awarded_date",
            serializer.errors,
        )


class StaffEmploymentSerializerTests(
    TestCase
):
    def test_rejects_invalid_dates(self):
        serializer = StaffEmploymentSerializer(
            data={
                "staff_member": (
                    StaffMemberFactory().pk
                ),
                "department": (
                    DepartmentFactory().pk
                ),
                "position": (
                    StaffPositionFactory().pk
                ),
                "employment_type": "primary",
                "rate": "1.00",
                "start_date": "2025-09-01",
                "end_date": "2025-08-31",
                "is_primary": False,
                "is_active": True,
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "end_date",
            serializer.errors,
        )

    def test_rejects_second_primary(self):
        member = StaffMemberFactory()

        StaffEmploymentFactory.primary(
            staff_member=member,
        )

        serializer = StaffEmploymentSerializer(
            data={
                "staff_member": member.pk,
                "department": (
                    DepartmentFactory().pk
                ),
                "position": (
                    StaffPositionFactory().pk
                ),
                "employment_type": "primary",
                "rate": "1.00",
                "start_date": "2025-09-01",
                "is_primary": True,
                "is_active": True,
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "is_primary",
            serializer.errors,
        )


class AcademicYearRecordSerializerTests(
    TestCase
):
    def test_rejects_duplicate_record(self):
        existing = (
            StaffEmploymentAcademicYearFactory()
        )

        serializer = (
            StaffEmploymentAcademicYearSerializer(
                data={
                    "staff_employment": (
                        existing.staff_employment_id
                    ),
                    "academic_year": (
                        existing.academic_year_id
                    ),
                    "rate": "1.00",
                    "is_active": True,
                }
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "non_field_errors",
            serializer.errors,
        )

        self.assertEqual(
            serializer.errors[
                "non_field_errors"
            ][0].code,
            "unique",
        )

    def test_rejects_inactive_degree(self):
        degree = AcademicDegreeFactory(
            is_active=False,
        )

        serializer = (
            StaffEmploymentAcademicYearSerializer(
                data={
                    "staff_employment": (
                        StaffEmploymentFactory().pk
                    ),
                    "academic_year": (
                        AcademicYearFactory().pk
                    ),
                    "rate": "1.00",
                    "academic_degree": degree.pk,
                    "is_active": True,
                }
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "academic_degree",
            serializer.errors,
        )


class WorkloadNormSerializerTests(
    TestCase
):
    def test_accepts_valid_norm(self):
        serializer = WorkloadNormSerializer(
            data={
                "academic_year": (
                    AcademicYearFactory().pk
                ),
                "rate": "1.00",
                "has_academic_degree": True,
                "has_academic_title": True,
                "annual_hours": "800.00",
                "is_active": True,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )