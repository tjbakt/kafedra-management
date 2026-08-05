from django.urls import reverse
from rest_framework import status

from apps.organizations.models import (
    Department,
)
from tests.base import BaseAPITestCase
from tests.factories import (
    DepartmentFactory,
)


class BaseArchiveViewSetIntegrationTests(
    BaseAPITestCase
):
    def setUp(self):
        self.user = self.create_global_admin()

        self.authenticate_with_jwt(
            user=self.user
        )

    def results(self, response):
        if isinstance(response.data, list):
            return response.data

        return response.data["results"]

    def test_delete_archives_record(self):
        department = DepartmentFactory()

        response = self.client.delete(
            reverse(
                "department-detail",
                kwargs={"pk": department.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        department.refresh_from_db()

        self.assertTrue(
            department.is_archived
        )
        self.assertEqual(
            department.archived_by,
            self.user,
        )
        self.assertIn(
            "detail",
            response.data,
        )

    def test_archived_list_contains_record(
        self,
    ):
        department = DepartmentFactory()
        department.archive(user=self.user)

        response = self.client.get(
            reverse("department-archived")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertIn(
            department.pk,
            ids,
        )

    def test_active_list_excludes_archived(
        self,
    ):
        department = DepartmentFactory()
        department.archive(user=self.user)

        response = self.client.get(
            reverse("department-list")
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertNotIn(
            department.pk,
            ids,
        )

    def test_restore_archived_record(self):
        department = DepartmentFactory()
        department.archive(user=self.user)

        response = self.client.post(
            reverse(
                "department-restore",
                kwargs={"pk": department.pk},
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["detail"],
            "Запись восстановлена из архива.",
        )
        self.assertEqual(
            response.data["data"]["id"],
            department.pk,
        )

        department.refresh_from_db()

        self.assertFalse(
            department.is_archived
        )
        self.assertEqual(
            department.updated_by,
            self.user,
        )

    def test_restore_active_record_returns_404(
        self,
    ):
        department = DepartmentFactory()

        response = self.client.post(
            reverse(
                "department-restore",
                kwargs={"pk": department.pk},
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_restore_unknown_record_returns_404(
        self,
    ):
        response = self.client.post(
            reverse(
                "department-restore",
                kwargs={"pk": 999999},
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_archived_list_requires_auth(
        self,
    ):
        self.logout_client()

        response = self.client.get(
            reverse("department-archived")
        )

        self.assertIn(
            response.status_code,
            (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ),
        )