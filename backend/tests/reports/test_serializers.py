from django.test import TestCase

from apps.reports.api.serializers import (
    DepartmentWorkloadReportRequestSerializer,
    TeacherWorkloadReportRequestSerializer,
)
from tests.factories import (
    AcademicYearFactory,
    DepartmentFactory,
    StaffEmploymentFactory,
    StaffPositionFactory,
)


class TeacherWorkloadReportSerializerTests(
    TestCase
):
    def test_accepts_teaching_employment(self):
        employment = StaffEmploymentFactory(
            position=StaffPositionFactory(
                is_teaching_position=True,
            ),
            is_active=True,
        )
        academic_year = AcademicYearFactory()

        serializer = (
            TeacherWorkloadReportRequestSerializer(
                data={
                    "staff_employment": (
                        employment.pk
                    ),
                    "academic_year": (
                        academic_year.pk
                    ),
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_rejects_non_teaching_position(
        self,
    ):
        employment = StaffEmploymentFactory(
            position=StaffPositionFactory(
                is_teaching_position=False,
            ),
        )

        serializer = (
            TeacherWorkloadReportRequestSerializer(
                data={
                    "staff_employment": (
                        employment.pk
                    ),
                    "academic_year": (
                        AcademicYearFactory().pk
                    ),
                }
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "staff_employment",
            serializer.errors,
        )

    def test_rejects_inactive_employment(
        self,
    ):
        employment = StaffEmploymentFactory(
            is_active=False,
        )

        serializer = (
            TeacherWorkloadReportRequestSerializer(
                data={
                    "staff_employment": (
                        employment.pk
                    ),
                    "academic_year": (
                        AcademicYearFactory().pk
                    ),
                }
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "staff_employment",
            serializer.errors,
        )

    def test_requires_both_parameters(self):
        serializer = (
            TeacherWorkloadReportRequestSerializer(
                data={}
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "staff_employment",
            serializer.errors,
        )
        self.assertIn(
            "academic_year",
            serializer.errors,
        )


class DepartmentWorkloadReportSerializerTests(
    TestCase
):
    def test_accepts_valid_request(self):
        department = DepartmentFactory()
        academic_year = AcademicYearFactory()

        serializer = (
            DepartmentWorkloadReportRequestSerializer(
                data={
                    "department": department.pk,
                    "academic_year": (
                        academic_year.pk
                    ),
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_rejects_archived_department(
        self,
    ):
        department = DepartmentFactory()
        department.archive()

        serializer = (
            DepartmentWorkloadReportRequestSerializer(
                data={
                    "department": department.pk,
                    "academic_year": (
                        AcademicYearFactory().pk
                    ),
                }
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "department",
            serializer.errors,
        )