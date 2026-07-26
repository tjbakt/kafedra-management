from decimal import Decimal
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.staff.models import (
    StaffEmploymentAcademicYear,
)
from apps.staff.tests.factories import (
    create_academic_year,
    create_employment,
    create_user,
)



class StaffEmploymentAcademicYearApiTests(
    APITestCase
):
    def setUp(self):
        self.user = create_user()
        self.academic_year = create_academic_year()
        self.employment = create_employment()

        self.list_url = reverse(
            "staff-employment-academic-year-list"
        )

        self.payload = {
            "staff_employment": (
                self.employment.pk
            ),
            "academic_year": (
                self.academic_year.pk
            ),
            "rate": "1.00",
            "academic_degree": None,
            "academic_title": None,
            "is_active": True,
            "notes": "",
        }

        self.client.force_authenticate(
            user=self.user
        )

        self.department_id = self.employment.department_id

    @patch(
        "apps.staff.api.views."
        "AccessService.can_manage_department",
        return_value=False,
    )
    @patch(
        "apps.staff.api.views."
        "AccessService.has_global_role",
        return_value=False,
    )
    def test_user_without_management_rights_cannot_create(
        self,
        mock_global_role,
        mock_department_access,
    ):
        response = self.client.post(
            self.list_url,
            self.payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertFalse(
            StaffEmploymentAcademicYear
            .objects
            .exists()
        )

    @patch(
        "apps.staff.api.views."
        "AccessService.can_manage_department",
        return_value=True,
    )
    @patch(
        "apps.staff.api.views."
        "AccessService.has_global_role",
        return_value=False,
    )
    def test_department_manager_can_create(
        self,
        mock_global_role,
        mock_department_access,
    ):
        response = self.client.post(
            self.list_url,
            self.payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        record = (
            StaffEmploymentAcademicYear
            .objects
            .get()
        )

        self.assertEqual(
            record.created_by,
            self.user,
        )
        self.assertEqual(
            record.updated_by,
            self.user,
        )

    @patch(
        "apps.staff.api.views."
        "AccessService.can_manage_department",
        return_value=False,
    )
    @patch(
        "apps.staff.api.views."
        "AccessService.has_global_role",
        return_value=False,
    )
    def test_user_without_rights_cannot_archive(
        self,
        mock_global_role,
        mock_department_access,
        mock_department_ids,
        mock_staff_ids,
    ):
        mock_department_ids.return_value = [self.employment.department_id]
        record = (
            StaffEmploymentAcademicYear
            .objects
            .create(
                staff_employment=self.employment,
                academic_year=self.academic_year,
                rate=Decimal("1.00"),
            )
        )

        detail_url = reverse(
            "staff-employment-academic-year-detail",
            args=(record.pk,),
        )

        response = self.client.delete(detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        record.refresh_from_db()

        self.assertFalse(record.is_archived)

    @patch(
        "apps.staff.api.views."
        "AccessService.accessible_staff_member_ids",
        return_value=[],
    )
    @patch(
        "apps.staff.api.views."
        "AccessService.accessible_department_ids",
        # return_value=[dept_id],
    )
    @patch(
        "apps.staff.api.views."
        "AccessService.has_global_role",
        return_value=False,
    )
    def test_archived_endpoint_does_not_expose_all_records(
            self,
            mock_global_role,
            mock_department_ids,
            mock_staff_ids,
    ):
        record = (
            StaffEmploymentAcademicYear.objects.create(
                staff_employment=self.employment,
                academic_year=self.academic_year,
                rate=Decimal("1.00"),
            )
        )
        record.archive(user=self.user)

        archived_url = reverse(
            "staff-employment-academic-year-archived"
        )

        response = self.client.get(archived_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data.get(
            "results",
            response.data,
        )

        self.assertEqual(results, [])

    @patch(
        "apps.staff.api.views."
        "AccessService.can_manage_department",
        return_value=False,
    )
    @patch(
        "apps.staff.api.views."
        "AccessService.has_global_role",
        return_value=False,
    )
    def test_user_without_rights_cannot_restore(
            self,
            mock_global_role,
            mock_department_access,
            mock_department_ids,
            mock_staff_ids,
    ):
        mock_department_ids.return_value = [self.employment.department_id]

        record = (
            StaffEmploymentAcademicYear.objects.create(
                staff_employment=self.employment,
                academic_year=self.academic_year,
                rate=Decimal("1.00"),
            )
        )
        record.archive(user=self.user)

        restore_url = reverse(
            "staff-employment-academic-year-restore",
            args=(record.pk,),
        )

        response = self.client.post(restore_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        record.refresh_from_db()

        self.assertTrue(record.is_archived)

    @patch(
        "apps.staff.api.views.AccessService.accessible_staff_member_ids",
        return_value=[],
    )
    @patch(
        "apps.staff.api.views.AccessService.accessible_department_ids",
    )
    @patch(
        "apps.staff.api.views."
        "AccessService.can_manage_department",
        return_value=True,
    )
    @patch(
        "apps.staff.api.views."
        "AccessService.has_global_role",
        return_value=False,
    )
    def test_department_manager_can_restore(
            self,
            mock_global_role,
            mock_department_access,
            mock_department_ids,
            mock_staff_ids,
    ):
        mock_department_ids.return_value = [self.employment.department_id]

        record = (
            StaffEmploymentAcademicYear.objects.create(
                staff_employment=self.employment,
                academic_year=self.academic_year,
                rate=Decimal("1.00"),
            )
        )
        record.archive(user=self.user)

        restore_url = reverse(
            "staff-employment-academic-year-restore",
            args=(record.pk,),
        )

        response = self.client.post(restore_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        record.refresh_from_db()

        self.assertFalse(record.is_archived)

    @patch(
        "apps.staff.api.views."
        "AccessService.can_manage_department",
        return_value=True,
    )
    @patch(
        "apps.staff.api.views."
        "AccessService.has_global_role",
        return_value=False,
    )
    def test_department_manager_can_create_missing_records(
            self,
            mock_global_role,
            mock_manage_department,
    ):
        url = reverse(
            (
                "staff-employment-academic-year-"
                "create-missing"
            )
        )

        response = self.client.post(
            url,
            {
                "academic_year": (
                    self.academic_year.id
                ),
                "department": (
                    self.employment.department_id
                ),
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
            StaffEmploymentAcademicYear.objects.filter(
                staff_employment=self.employment,
                academic_year=self.academic_year,
            ).exists()
        )

    @patch(
        "apps.staff.api.views."
        "AccessService.has_global_role",
        return_value=False,
    )
    def test_department_manager_cannot_fill_all_departments(
            self,
            mock_global_role,
    ):
        url = reverse(
            (
                "staff-employment-academic-year-"
                "create-missing"
            )
        )

        response = self.client.post(
            url,
            {
                "academic_year": (
                    self.academic_year.id
                ),
                "department": None,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            StaffEmploymentAcademicYear
            .objects
            .exists()
        )

    @patch(
        "apps.staff.api.views."
        "AccessService.can_manage_department",
        return_value=True,
    )
    @patch(
        "apps.staff.api.views."
        "AccessService.has_global_role",
        return_value=False,
    )
    def test_repeated_bulk_request_does_not_duplicate_records(
            self,
            mock_global_role,
            mock_manage_department,
    ):
        url = reverse(
            (
                "staff-employment-academic-year-"
                "create-missing"
            )
        )

        payload = {
            "academic_year": self.academic_year.id,
            "department": (
                self.employment.department_id
            ),
        }

        first_response = self.client.post(
            url,
            payload,
            format="json",
        )
        second_response = self.client.post(
            url,
            payload,
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            first_response.data["created"],
            1,
        )
        self.assertEqual(
            second_response.data["created"],
            0,
        )
        self.assertEqual(
            second_response.data["skipped"],
            1,
        )

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

    @patch(
        "apps.staff.api.views."
        "AccessService.accessible_department_ids",
        return_value=[1],
    )
    @patch(
        "apps.staff.api.views."
        "AccessService.has_global_role",
        return_value=False,
    )
    def test_missing_returns_employment_without_year_record(
            self,
            mock_global_role,
            mock_department_ids,
    ):
        department_id = (
            self.employment.department_id
        )

        mock_department_ids.return_value = [
            department_id
        ]

        url = reverse(
            (
                "staff-employment-academic-year-"
                "missing"
            )
        )

        response = self.client.get(
            url,
            {
                "academic_year": (
                    self.academic_year.id
                ),
                "department": department_id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data.get(
            "results",
            response.data,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["staff_employment"],
            self.employment.id,
        )