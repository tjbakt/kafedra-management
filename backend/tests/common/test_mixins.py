from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.test import TestCase
from rest_framework import serializers
from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
)
from rest_framework.test import (
    APIRequestFactory,
)
from rest_framework.viewsets import (
    GenericViewSet,
)

from apps.common.api.mixins import (
    ArchiveModelMixin,
    DjangoValidationErrorMixin,
    UserAuditMixin,
)
from apps.organizations.api.serializers import (
    DepartmentSerializer,
)
from tests.factories import (
    DepartmentFactory,
    UserFactory,
)


class DummyAuditView(
    UserAuditMixin,
    GenericViewSet,
):
    serializer_class = DepartmentSerializer


class DummyValidationView(
    DjangoValidationErrorMixin,
    GenericViewSet,
):
    pass


class DummyArchiveView(
    ArchiveModelMixin,
    GenericViewSet,
):
    archive_response_message = (
        "Тестовая запись архивирована."
    )


class UserAuditMixinTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserFactory()

    def create_view(self):
        request = self.factory.post(
            "/test/",
            {},
            format="json",
        )
        request.user = self.user

        view = DummyAuditView()
        view.request = request

        return view

    def test_perform_create_sets_audit_users(
        self,
    ):
        view = self.create_view()

        serializer = (
            DepartmentSerializer(
                data={
                    "faculty": (
                        DepartmentFactory()
                        .faculty_id
                    ),
                    "code": "COMMON-AUDIT",
                    "name_ru": (
                        "Тестовая кафедра"
                    ),
                    "name_uz": (
                        "Test kafedrasi"
                    ),
                    "is_active": True,
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        view.perform_create(serializer)

        instance = serializer.instance

        self.assertEqual(
            instance.created_by,
            self.user,
        )
        self.assertEqual(
            instance.updated_by,
            self.user,
        )

    def test_perform_update_sets_updated_by(
        self,
    ):
        view = self.create_view()
        department = DepartmentFactory()

        serializer = DepartmentSerializer(
            department,
            data={
                "name_ru": (
                    "Изменённая кафедра"
                ),
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        view.perform_update(serializer)

        department.refresh_from_db()

        self.assertEqual(
            department.updated_by,
            self.user,
        )


class ArchiveModelMixinTests(TestCase):
    def test_perform_destroy_archives(self):
        user = UserFactory()
        department = DepartmentFactory()

        view = DummyArchiveView()

        request = APIRequestFactory().delete(
            "/test/"
        )
        request.user = user
        view.request = request

        view.perform_destroy(department)
        department.refresh_from_db()

        self.assertTrue(
            department.is_archived
        )
        self.assertEqual(
            department.archived_by,
            user,
        )


class DjangoValidationErrorMixinTests(
    TestCase
):
    def setUp(self):
        self.factory = APIRequestFactory()

    def create_view(self):
        request = self.factory.get(
            "/test/"
        )

        view = DummyValidationView()
        view.request = request
        view.headers = {}
        view.format_kwarg = None

        return view

    def assert_validation_envelope(
        self,
        response,
    ):
        self.assertEqual(
            response.status_code,
            400,
        )
        self.assertFalse(
            response.data["success"]
        )
        self.assertEqual(
            response.data["status_code"],
            400,
        )
        self.assertEqual(
            response.data["error"]["code"],
            "validation_error",
        )

    def test_message_dict_is_converted(self):
        view = self.create_view()

        response = view.handle_exception(
            DjangoValidationError(
                {
                    "name_ru": [
                        "Некорректное название."
                    ]
                }
            )
        )

        self.assert_validation_envelope(
            response
        )

        error = response.data["error"]

        self.assertEqual(
            error["message"],
            "Некорректное название.",
        )
        self.assertIsNone(
            error["details"]
        )

        fields = error["fields"]

        self.assertIn(
            "name_ru",
            fields,
        )
        self.assertEqual(
            fields["name_ru"][0],
            {
                "message": (
                    "Некорректное название."
                ),
                "code": "invalid",
            },
        )

    def test_message_list_is_converted(self):
        view = self.create_view()

        response = view.handle_exception(
            DjangoValidationError(
                "Общая ошибка."
            )
        )

        self.assert_validation_envelope(
            response
        )

        error = response.data["error"]

        self.assertEqual(
            error["message"],
            "Общая ошибка.",
        )
        self.assertIsNone(
            error["fields"]
        )
        self.assertIsNone(
            error["details"]
        )