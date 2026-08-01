from types import SimpleNamespace

from django.test import TestCase
from rest_framework.exceptions import (
    ValidationError,
)

from apps.accounts.api.serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    UserSerializer,
)
from tests.factories import UserFactory


class UserSerializerTests(TestCase):
    def test_contains_expected_fields(self):
        user = UserFactory(
            username="serializer_user",
            email="serializer@example.com",
            first_name="Иван",
            last_name="Иванов",
            middle_name="Иванович",
        )

        serializer = UserSerializer(user)

        expected_fields = {
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "middle_name",
            "full_name",
            "phone",
            "avatar",
            "interface_language",
            "must_change_password",
            "is_active",
            "is_staff",
            "groups",
            "permissions",
            "last_login",
            "created_at",
            "updated_at",
        }

        self.assertEqual(
            set(serializer.data),
            expected_fields,
        )

    def test_read_only_fields_cannot_be_changed(self):
        user = UserFactory(
            username="readonly_user",
            is_staff=False,
            is_active=True,
            must_change_password=False,
        )

        serializer = UserSerializer(
            user,
            data={
                "username": "changed_username",
                "is_staff": True,
                "is_active": False,
                "must_change_password": True,
                "first_name": "Новое имя",
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        updated_user = serializer.save()

        self.assertEqual(
            updated_user.username,
            "readonly_user",
        )
        self.assertFalse(
            updated_user.is_staff
        )
        self.assertTrue(
            updated_user.is_active
        )
        self.assertFalse(
            updated_user.must_change_password
        )
        self.assertEqual(
            updated_user.first_name,
            "Новое имя",
        )

    def test_groups_and_permissions_are_lists(self):
        user = UserFactory()

        serializer = UserSerializer(user)

        self.assertIsInstance(
            serializer.data["groups"],
            list,
        )
        self.assertIsInstance(
            serializer.data["permissions"],
            list,
        )


class LogoutSerializerTests(TestCase):
    def test_accepts_refresh_token(self):
        serializer = LogoutSerializer(
            data={
                "refresh": "test-refresh-token",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_rejects_missing_refresh_token(self):
        serializer = LogoutSerializer(
            data={}
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "refresh",
            serializer.errors,
        )

    def test_rejects_blank_refresh_token(self):
        serializer = LogoutSerializer(
            data={
                "refresh": "",
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "refresh",
            serializer.errors,
        )


class ChangePasswordSerializerTests(TestCase):
    current_password = "Current-password-123"
    new_password = "New-password-456"

    def setUp(self):
        self.user = UserFactory(
            password=self.current_password
        )

        self.request = SimpleNamespace(
            user=self.user
        )

    def build_serializer(
        self,
        data,
    ):
        return ChangePasswordSerializer(
            data=data,
            context={
                "request": self.request,
            },
        )

    def test_accepts_valid_password_change(self):
        serializer = self.build_serializer(
            {
                "current_password": (
                    self.current_password
                ),
                "new_password": (
                    self.new_password
                ),
                "new_password_confirmation": (
                    self.new_password
                ),
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_rejects_wrong_current_password(self):
        serializer = self.build_serializer(
            {
                "current_password": (
                    "Wrong-password-123"
                ),
                "new_password": (
                    self.new_password
                ),
                "new_password_confirmation": (
                    self.new_password
                ),
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "current_password",
            serializer.errors,
        )

    def test_rejects_password_confirmation_mismatch(
        self,
    ):
        serializer = self.build_serializer(
            {
                "current_password": (
                    self.current_password
                ),
                "new_password": (
                    self.new_password
                ),
                "new_password_confirmation": (
                    "Another-password-789"
                ),
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "new_password_confirmation",
            serializer.errors,
        )

    def test_rejects_short_password(self):
        serializer = self.build_serializer(
            {
                "current_password": (
                    self.current_password
                ),
                "new_password": "123",
                "new_password_confirmation": "123",
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "new_password",
            serializer.errors,
        )

    def test_rejects_common_password(self):
        serializer = self.build_serializer(
            {
                "current_password": (
                    self.current_password
                ),
                "new_password": "password",
                "new_password_confirmation": (
                    "password"
                ),
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "new_password",
            serializer.errors,
        )


class CustomTokenSerializerTests(TestCase):
    password = "Login-password-123"

    def test_token_contains_custom_claims(self):
        user = UserFactory(
            username="token_claim_user",
            first_name="Анна",
            last_name="Петрова",
            interface_language="ru",
            password=self.password,
        )

        token = (
            CustomTokenObtainPairSerializer
            .get_token(user)
        )

        self.assertEqual(
            token["username"],
            user.username,
        )
        self.assertEqual(
            token["full_name"],
            user.full_name,
        )
        self.assertEqual(
            token["language"],
            user.interface_language,
        )
        self.assertEqual(
            token["groups"],
            [],
        )

    def test_validate_returns_user_data(self):
        user = UserFactory(
            username="token_validate_user",
            password=self.password,
        )

        serializer = (
            CustomTokenObtainPairSerializer(
                data={
                    "username": user.username,
                    "password": self.password,
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertIn(
            "access",
            serializer.validated_data,
        )
        self.assertIn(
            "refresh",
            serializer.validated_data,
        )
        self.assertIn(
            "user",
            serializer.validated_data,
        )

        self.assertEqual(
            serializer.validated_data[
                "user"
            ]["id"],
            user.pk,
        )