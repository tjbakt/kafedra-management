from django.urls import reverse
from rest_framework import status

from apps.organizations.models import (
    Department,
    Faculty,
    University,
)
from tests.assertions import (
    ApiResponseAssertionsMixin,
)
from tests.base import BaseAPITestCase
from tests.factories import (
    DepartmentFactory,
    FacultyFactory,
    UniversityFactory,
    UserFactory,
)


class OrganizationApiBaseTestCase(
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


class UniversityApiTests(
    OrganizationApiBaseTestCase
):
    def setUp(self):
        super().setUp()

        self.list_url = reverse(
            "university-list"
        )

    def detail_url(self, university):
        return reverse(
            "university-detail",
            kwargs={
                "pk": university.pk,
            },
        )

    def restore_url(self, university):
        return reverse(
            "university-restore",
            kwargs={
                "pk": university.pk,
            },
        )

    def valid_payload(self, suffix="1"):
        return {
            "code": f"UNI-API-{suffix}",
            "name_ru": (
                f"Университет API {suffix}"
            ),
            "name_uz": (
                f"API universiteti {suffix}"
            ),
            "short_name_ru": "УАПИ",
            "short_name_uz": "UAPI",
            "address_ru": "",
            "address_uz": "",
            "phone": "",
            "email": (
                f"university-{suffix}@example.com"
            ),
            "website": "",
            "is_active": True,
            "sort_order": 0,
        }

    def test_list_requires_authentication(self):
        self.logout_client()

        response = self.client.get(
            self.list_url
        )

        self.assert_authentication_required(
            response
        )

    def test_list_is_paginated(self):
        UniversityFactory.create_batch(3)

        response = self.client.get(
            self.list_url
        )

        data = self.assert_paginated_response(
            response
        )

        self.assertGreaterEqual(
            data["count"],
            3,
        )

    def test_create_sets_audit_fields(self):
        response = self.client.post(
            self.list_url,
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        university = University.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            university.created_by,
            self.user,
        )
        self.assertEqual(
            university.updated_by,
            self.user,
        )
        self.assertEqual(
            university.code,
            "UNI-API-1",
        )

    def test_any_authenticated_user_can_create(self):
        response = self.client.post(
            self.list_url,
            self.valid_payload("AUTH"),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_create_normalizes_code(self):
        payload = self.valid_payload("NORMAL")
        payload["code"] = "  uni-normal  "

        response = self.client.post(
            self.list_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["code"],
            "UNI-NORMAL",
        )

    def test_duplicate_code_is_rejected(self):
        UniversityFactory(
            code="UNI-DUPLICATE",
        )

        payload = self.valid_payload("DUP")
        payload["code"] = "UNI-DUPLICATE"

        response = self.client.post(
            self.list_url,
            payload,
            format="json",
        )

        self.assert_validation_error(
            response,
            field="code",
        )

    def test_retrieve_returns_faculties_count(self):
        university = UniversityFactory()
        FacultyFactory.create_batch(
            2,
            university=university,
        )

        response = self.client.get(
            self.detail_url(university)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["faculties_count"],
            2,
        )

    def test_patch_updates_updated_by(self):
        university = UniversityFactory()
        new_user = UserFactory()

        self.authenticate_with_jwt(
            user=new_user
        )

        response = self.client.patch(
            self.detail_url(university),
            {
                "name_ru": (
                    "Изменённый университет"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        university.refresh_from_db()

        self.assertEqual(
            university.name_ru,
            "Изменённый университет",
        )
        self.assertEqual(
            university.updated_by,
            new_user,
        )

    def test_delete_archives_object(self):
        university = UniversityFactory()

        response = self.client.delete(
            self.detail_url(university)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["detail"],
            "Запись перемещена в архив.",
        )

        university = (
            University.all_objects.get(
                pk=university.pk
            )
        )

        self.assertTrue(
            university.is_archived
        )
        self.assertEqual(
            university.archived_by,
            self.user,
        )

    def test_archived_object_is_hidden_from_list(
        self,
    ):
        university = UniversityFactory()
        university.archive(user=self.user)

        response = self.client.get(
            self.list_url
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertNotIn(
            university.pk,
            ids,
        )

    def test_archived_endpoint_returns_object(self):
        university = UniversityFactory()
        university.archive(user=self.user)

        response = self.client.get(
            reverse("university-archived")
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
            university.pk,
            ids,
        )

    def test_restore_returns_object_to_active_list(
        self,
    ):
        university = UniversityFactory()
        university.archive(user=self.user)

        response = self.client.post(
            self.restore_url(university),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        university.refresh_from_db()

        self.assertFalse(
            university.is_archived
        )
        self.assertEqual(
            university.updated_by,
            self.user,
        )

    def test_query_filter(self):
        expected = UniversityFactory(
            code="UNIQUE-QUERY-CODE",
        )
        UniversityFactory(
            code="ANOTHER-CODE",
        )

        response = self.client.get(
            self.list_url,
            {
                "query": "unique-query",
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

    def test_is_active_filter(self):
        active = UniversityFactory(
            is_active=True,
        )
        UniversityFactory(
            is_active=False,
        )

        response = self.client.get(
            self.list_url,
            {
                "is_active": "true",
            },
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertIn(
            active.pk,
            ids,
        )

    def test_search_filter(self):
        expected = UniversityFactory(
            name_ru="Уникальный университет поиска",
        )
        UniversityFactory(
            name_ru="Другое название",
        )

        response = self.client.get(
            self.list_url,
            {
                "search": "Уникальный",
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


class FacultyApiTests(
    OrganizationApiBaseTestCase
):
    def setUp(self):
        super().setUp()

        self.university = UniversityFactory()
        self.list_url = reverse(
            "faculty-list"
        )

    def detail_url(self, faculty):
        return reverse(
            "faculty-detail",
            kwargs={
                "pk": faculty.pk,
            },
        )

    def valid_payload(self, suffix="1"):
        return {
            "university": self.university.pk,
            "faculty_type": "standard",
            "code": f"FAC-API-{suffix}",
            "name_ru": (
                f"Факультет API {suffix}"
            ),
            "name_uz": (
                f"API fakulteti {suffix}"
            ),
            "short_name_ru": "",
            "short_name_uz": "",
            "dean_name": "",
            "phone": "",
            "email": (
                f"faculty-{suffix}@example.com"
            ),
            "is_active": True,
            "sort_order": 0,
        }

    def test_create_faculty(self):
        response = self.client.post(
            self.list_url,
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        faculty = Faculty.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            faculty.university,
            self.university,
        )
        self.assertEqual(
            faculty.created_by,
            self.user,
        )

    def test_create_rejects_archived_university(
        self,
    ):
        self.university.archive(
            user=self.user
        )

        response = self.client.post(
            self.list_url,
            self.valid_payload(),
            format="json",
        )

        self.assert_validation_error(
            response,
            field="university",
        )

    def test_filter_by_university(self):
        expected = FacultyFactory(
            university=self.university,
        )
        FacultyFactory()

        response = self.client.get(
            self.list_url,
            {
                "university": (
                    self.university.pk
                ),
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

    def test_filter_by_faculty_type(self):
        expected = FacultyFactory(
            university=self.university,
            faculty_type="magistracy",
        )
        FacultyFactory(
            university=self.university,
            faculty_type="standard",
        )

        response = self.client.get(
            self.list_url,
            {
                "faculty_type": (
                    "magistracy"
                ),
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

    def test_departments_count_excludes_archived(
        self,
    ):
        faculty = FacultyFactory(
            university=self.university,
        )
        DepartmentFactory(
            faculty=faculty,
        )
        archived = DepartmentFactory(
            faculty=faculty,
        )
        archived.archive(user=self.user)

        response = self.client.get(
            self.detail_url(faculty)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["departments_count"],
            1,
        )

    def test_delete_and_restore_faculty(self):
        faculty = FacultyFactory(
            university=self.university,
        )

        delete_response = self.client.delete(
            self.detail_url(faculty)
        )

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_200_OK,
        )

        restore_response = self.client.post(
            reverse(
                "faculty-restore",
                kwargs={
                    "pk": faculty.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            restore_response.status_code,
            status.HTTP_200_OK,
        )

        faculty.refresh_from_db()

        self.assertFalse(
            faculty.is_archived
        )


class DepartmentApiTests(
    OrganizationApiBaseTestCase
):
    def setUp(self):
        super().setUp()

        self.university = UniversityFactory()
        self.faculty = FacultyFactory(
            university=self.university,
        )
        self.list_url = reverse(
            "department-list"
        )

    def detail_url(self, department):
        return reverse(
            "department-detail",
            kwargs={
                "pk": department.pk,
            },
        )

    def valid_payload(self, suffix="1"):
        return {
            "faculty": self.faculty.pk,
            "code": f"DEP-API-{suffix}",
            "name_ru": (
                f"Кафедра API {suffix}"
            ),
            "name_uz": (
                f"API kafedrasi {suffix}"
            ),
            "short_name_ru": "",
            "short_name_uz": "",
            "head_name": "",
            "phone": "",
            "email": (
                f"department-{suffix}@example.com"
            ),
            "room": "",
            "is_active": True,
            "sort_order": 0,
        }

    def test_create_department(self):
        response = self.client.post(
            self.list_url,
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        department = Department.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            department.faculty,
            self.faculty,
        )
        self.assertEqual(
            department.created_by,
            self.user,
        )

        self.assertEqual(
            response.data["university"],
            self.university.pk,
        )

    def test_create_rejects_archived_faculty(self):
        self.faculty.archive(
            user=self.user
        )

        response = self.client.post(
            self.list_url,
            self.valid_payload(),
            format="json",
        )

        self.assert_validation_error(
            response,
            field="faculty",
        )

    def test_filter_by_university(self):
        expected = DepartmentFactory(
            faculty=self.faculty,
        )
        DepartmentFactory()

        response = self.client.get(
            self.list_url,
            {
                "university": (
                    self.university.pk
                ),
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

    def test_filter_by_faculty(self):
        expected = DepartmentFactory(
            faculty=self.faculty,
        )
        DepartmentFactory()

        response = self.client.get(
            self.list_url,
            {
                "faculty": self.faculty.pk,
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

    def test_patch_cannot_change_derived_university(
        self,
    ):
        department = DepartmentFactory(
            faculty=self.faculty,
        )
        another_university = (
            UniversityFactory()
        )

        response = self.client.patch(
            self.detail_url(department),
            {
                "university": (
                    another_university.pk
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        department.refresh_from_db()

        self.assertEqual(
            department.faculty,
            self.faculty,
        )
        self.assertEqual(
            response.data["university"],
            self.university.pk,
        )

    def test_delete_and_restore_department(self):
        department = DepartmentFactory(
            faculty=self.faculty,
        )

        delete_response = self.client.delete(
            self.detail_url(department)
        )

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_200_OK,
        )

        restore_response = self.client.post(
            reverse(
                "department-restore",
                kwargs={
                    "pk": department.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            restore_response.status_code,
            status.HTTP_200_OK,
        )

        department.refresh_from_db()

        self.assertFalse(
            department.is_archived
        )
        self.assertEqual(
            department.updated_by,
            self.user,
        )