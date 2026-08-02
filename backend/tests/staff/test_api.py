from decimal import Decimal

from django.urls import reverse
from rest_framework import status

from apps.access_control.models import (
    SystemRole,
)
from apps.staff.models import (
    StaffEmploymentAcademicYear,
)
from tests.assertions import (
    ApiResponseAssertionsMixin,
)
from tests.base import BaseAPITestCase
from tests.factories import (
    AcademicDegreeFactory,
    AcademicTitleFactory,
    AcademicYearFactory,
    DepartmentFactory,
    StaffEmploymentAcademicYearFactory,
    StaffEmploymentFactory,
    StaffMemberFactory,
    StaffPositionFactory,
    UserFactory,
    UserRoleAssignmentFactory,
    WorkloadNormFactory,
)


class StaffApiBase(
    ApiResponseAssertionsMixin,
    BaseAPITestCase,
):
    def setUp(self):
        self.user = UserFactory()

        self.authenticate_with_jwt(
            user=self.user
        )

    def results(self, response):
        if isinstance(response.data, list):
            return response.data

        return response.data["results"]


class StaffReferenceApiTests(
    StaffApiBase
):
    def test_create_position(self):
        response = self.client.post(
            reverse("staff-position-list"),
            {
                "code": " docent ",
                "name_ru": "Доцент",
                "name_uz": "Dotsent",
                "category": "teaching",
                "is_teaching_position": True,
                "is_active": True,
                "sort_order": 0,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["code"],
            "DOCENT",
        )

    def test_create_degree(self):
        response = self.client.post(
            reverse("academic-degree-list"),
            {
                "code": " phd ",
                "name_ru": "Доктор философии",
                "name_uz": "Falsafa doktori",
                "short_name_ru": "PhD",
                "short_name_uz": "PhD",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_create_title(self):
        response = self.client.post(
            reverse("academic-title-list"),
            {
                "code": " docent ",
                "name_ru": "Доцент",
                "name_uz": "Dotsent",
                "short_name_ru": "доц.",
                "short_name_uz": "dots.",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )


class StaffMemberApiTests(StaffApiBase):
    def test_anonymous_is_rejected(self):
        self.logout_client()

        response = self.client.get(
            reverse("staff-member-list")
        )

        self.assert_authentication_required(
            response
        )

    def test_create_member(self):
        response = self.client.post(
            reverse("staff-member-list"),
            {
                "personnel_number": " staff-api ",
                "last_name": "Иванов",
                "first_name": "Иван",
                "middle_name": "",
                "gender": "male",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["personnel_number"],
            "STAFF-API",
        )

    def test_department_head_sees_own_department(
        self,
    ):
        user = UserFactory()
        department = DepartmentFactory()

        UserRoleAssignmentFactory.department_role(
            user=user,
            department=department,
        )

        expected = StaffMemberFactory()
        StaffEmploymentFactory(
            staff_member=expected,
            department=department,
        )

        hidden = StaffMemberFactory()
        StaffEmploymentFactory(
            staff_member=hidden,
            department=DepartmentFactory(),
        )

        self.authenticate_with_jwt(
            user=user
        )

        response = self.client.get(
            reverse("staff-member-list")
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertIn(expected.pk, ids)
        self.assertNotIn(hidden.pk, ids)


class StaffEmploymentApiTests(
    StaffApiBase
):
    def test_create_employment(self):
        response = self.client.post(
            reverse("staff-employment-list"),
            {
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
                "is_primary": False,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_recommended_workload(self):
        year = AcademicYearFactory()
        degree = AcademicDegreeFactory()
        title = AcademicTitleFactory()

        member = StaffMemberFactory(
            academic_degree=degree,
            academic_title=title,
        )
        employment = StaffEmploymentFactory(
            staff_member=member,
            rate=Decimal("1.00"),
        )

        record = (
            StaffEmploymentAcademicYearFactory(
                staff_employment=employment,
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

        response = self.client.get(
            reverse(
                "staff-employment-recommended-workload",
                kwargs={
                    "pk": employment.pk,
                },
            ),
            {
                "academic_year": year.pk,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data[
                "academic_year_record"
            ],
            record.pk,
        )
        self.assertEqual(
            Decimal(
                response.data["annual_hours"]
            ),
            norm.annual_hours,
        )
        self.assertTrue(
            response.data["norm_found"]
        )

    def test_recommended_workload_requires_year(
        self,
    ):
        employment = StaffEmploymentFactory()

        response = self.client.get(
            reverse(
                "staff-employment-recommended-workload",
                kwargs={
                    "pk": employment.pk,
                },
            )
        )

        self.assert_validation_error(
            response,
            field="academic_year",
        )


class AcademicYearRecordApiTests(
    StaffApiBase
):
    def test_hr_can_create_record(self):
        hr_user = UserFactory()

        UserRoleAssignmentFactory.global_role(
            user=hr_user,
            role_code=(
                SystemRole.Code.HR_OFFICER
            ),
        )

        employment = StaffEmploymentFactory()
        year = AcademicYearFactory()

        self.authenticate_with_jwt(
            user=hr_user
        )

        response = self.client.post(
            reverse(
                "staff-employment-academic-year-list"
            ),
            {
                "staff_employment": employment.pk,
                "academic_year": year.pk,
                "rate": "1.00",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_unprivileged_user_cannot_create_record(
        self,
    ):
        employment = StaffEmploymentFactory()
        year = AcademicYearFactory()

        response = self.client.post(
            reverse(
                "staff-employment-academic-year-list"
            ),
            {
                "staff_employment": employment.pk,
                "academic_year": year.pk,
                "rate": "1.00",
                "is_active": True,
            },
            format="json",
        )

        self.assert_permission_denied(
            response
        )

    def test_hr_can_create_missing_records(self):
        hr_user = UserFactory()

        UserRoleAssignmentFactory.global_role(
            user=hr_user,
            role_code=(
                SystemRole.Code.HR_OFFICER
            ),
        )

        year = AcademicYearFactory()
        department = DepartmentFactory()

        employment = StaffEmploymentFactory(
            department=department,
            position=StaffPositionFactory(
                is_teaching_position=True,
            ),
        )

        self.authenticate_with_jwt(
            user=hr_user
        )

        response = self.client.post(
            reverse(
                "staff-employment-academic-year-create-missing"
            ),
            {
                "academic_year": year.pk,
                "department": department.pk,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["created"],
            1,
        )

        self.assertTrue(
            StaffEmploymentAcademicYear.objects
            .filter(
                staff_employment=employment,
                academic_year=year,
            )
            .exists()
        )


class WorkloadNormApiTests(
    StaffApiBase
):
    def test_create_norm(self):
        response = self.client.post(
            reverse("workload-norm-list"),
            {
                "academic_year": (
                    AcademicYearFactory().pk
                ),
                "rate": "1.00",
                "has_academic_degree": False,
                "has_academic_title": False,
                "annual_hours": "850.00",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_filter_norm(self):
        year = AcademicYearFactory()

        expected = WorkloadNormFactory(
            academic_year=year,
            rate=Decimal("1.00"),
            has_academic_degree=True,
            has_academic_title=False,
        )

        WorkloadNormFactory(
            academic_year=AcademicYearFactory(),
            rate=Decimal("0.50"),
        )

        response = self.client.get(
            reverse("workload-norm-list"),
            {
                "academic_year": year.pk,
                "rate": "1.00",
                "has_academic_degree": "true",
                "has_academic_title": "false",
            },
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertEqual(
            ids,
            {expected.pk},
        )