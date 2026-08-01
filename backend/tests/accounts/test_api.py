from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
)
from rest_framework_simplejwt.tokens import (
    AccessToken,
    RefreshToken,
)

from tests.assertions import (
    ApiResponseAssertionsMixin,
)
from tests.base import BaseAPITestCase
from tests.factories import UserFactory


class AccountApiBaseTestCase(
    ApiResponseAssertionsMixin,
    BaseAPITestCase,
):
    password = "Account-password-123"

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(
            username="account_api_user",
            email="account@example.com",
            first_name="Иван",
            last_name="Иванов",
            middle_name="Иванович",
            phone="+998900000001",
            interface_language="ru",
            must_change_password=True,
            password=cls.password,
        )

    def setUp(self):
        self.login_url = reverse(
            "accounts:login"
        )
        self.refresh_url = reverse(
            "accounts:token-refresh"
        )
        self.verify_url = reverse(
            "accounts:token-verify"
        )
        self.logout_url = reverse(
            "accounts:logout"
        )
        self.me_url = reverse(
            "accounts:current-user"
        )
        self.change_password_url = reverse(
            "accounts:change-password"
        )

    def issue_tokens(
        self,
        user=None,
    ):
        return RefreshToken.for_user(
            user or self.user
        )


class LoginApiTests(AccountApiBaseTestCase):
    def test_login_returns_access_refresh_and_user(
        self,
    ):
        response = self.client.post(
            self.login_url,
            {
                "username": self.user.username,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )
        self.assertIn(
            "refresh",
            response.data,
        )
        self.assertIn(
            "user",
            response.data,
        )

        self.assertEqual(
            response.data["user"]["id"],
            self.user.pk,
        )
        self.assertEqual(
            response.data["user"]["username"],
            self.user.username,
        )
        self.assertEqual(
            response.data["user"]["email"],
            self.user.email,
        )

    def test_access_token_contains_custom_claims(
        self,
    ):
        response = self.client.post(
            self.login_url,
            {
                "username": self.user.username,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        access_token = AccessToken(
            response.data["access"]
        )

        self.assertEqual(
            int(access_token["user_id"]),
            self.user.pk,
        )
        self.assertEqual(
            access_token["username"],
            self.user.username,
        )
        self.assertEqual(
            access_token["full_name"],
            self.user.full_name,
        )
        self.assertEqual(
            access_token["language"],
            self.user.interface_language,
        )
        self.assertEqual(
            access_token["groups"],
            [],
        )

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            self.login_url,
            {
                "username": self.user.username,
                "password": "Wrong-password-123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertFalse(
            response.data["success"]
        )
        self.assertEqual(
            response.data["status_code"],
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertIn(
            "error",
            response.data,
        )

    def test_login_rejects_missing_password(self):
        response = self.client.post(
            self.login_url,
            {
                "username": self.user.username,
            },
            format="json",
        )

        self.assert_validation_error(
            response,
            field="password",
        )

    def test_login_rejects_missing_username(self):
        response = self.client.post(
            self.login_url,
            {
                "password": self.password,
            },
            format="json",
        )

        self.assert_validation_error(
            response,
            field="username",
        )

    def test_inactive_user_cannot_login(self):
        inactive_user = UserFactory(
            username="inactive_login_user",
            is_active=False,
            password=self.password,
        )

        response = self.client.post(
            self.login_url,
            {
                "username": inactive_user.username,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class RefreshTokenApiTests(
    AccountApiBaseTestCase
):
    def test_refresh_returns_new_tokens(self):
        refresh = self.issue_tokens()

        response = self.client.post(
            self.refresh_url,
            {
                "refresh": str(refresh),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn(
            "access",
            response.data,
        )

        # В проекте включена ротация refresh-токенов.
        self.assertIn(
            "refresh",
            response.data,
        )

        AccessToken(
            response.data["access"]
        )
        RefreshToken(
            response.data["refresh"]
        )

    def test_used_refresh_is_blacklisted_after_rotation(
        self,
    ):
        refresh = self.issue_tokens()
        old_jti = refresh["jti"]

        response = self.client.post(
            self.refresh_url,
            {
                "refresh": str(refresh),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            BlacklistedToken.objects.filter(
                token__jti=old_jti
            ).exists()
        )

    def test_refresh_rejects_invalid_token(self):
        response = self.client.post(
            self.refresh_url,
            {
                "refresh": "invalid-token",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertFalse(
            response.data["success"]
        )

    def test_refresh_requires_token(self):
        response = self.client.post(
            self.refresh_url,
            {},
            format="json",
        )

        self.assert_validation_error(
            response,
            field="refresh",
        )


class VerifyTokenApiTests(
    AccountApiBaseTestCase
):
    def test_verify_accepts_access_token(self):
        refresh = self.issue_tokens()

        response = self.client.post(
            self.verify_url,
            {
                "token": str(
                    refresh.access_token
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data,
            {},
        )

    def test_verify_accepts_refresh_token(self):
        refresh = self.issue_tokens()

        response = self.client.post(
            self.verify_url,
            {
                "token": str(refresh),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_verify_rejects_invalid_token(self):
        response = self.client.post(
            self.verify_url,
            {
                "token": "invalid-token",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertFalse(
            response.data["success"]
        )

    def test_verify_requires_token(self):
        response = self.client.post(
            self.verify_url,
            {},
            format="json",
        )

        self.assert_validation_error(
            response,
            field="token",
        )


class LogoutApiTests(AccountApiBaseTestCase):
    def test_logout_requires_authentication(self):
        refresh = self.issue_tokens()

        response = self.client.post(
            self.logout_url,
            {
                "refresh": str(refresh),
            },
            format="json",
        )

        self.assert_authentication_required(
            response
        )

    def test_logout_blacklists_refresh_token(self):
        refresh = self.issue_tokens()
        jti = refresh["jti"]

        self.authenticate_with_jwt(
            user=self.user
        )

        response = self.client.post(
            self.logout_url,
            {
                "refresh": str(refresh),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertEqual(
            response.content,
            b"",
        )

        self.assertTrue(
            BlacklistedToken.objects.filter(
                token__jti=jti
            ).exists()
        )

    def test_blacklisted_refresh_cannot_be_used(
        self,
    ):
        refresh = self.issue_tokens()

        self.authenticate_with_jwt(
            user=self.user
        )

        logout_response = self.client.post(
            self.logout_url,
            {
                "refresh": str(refresh),
            },
            format="json",
        )

        self.assertEqual(
            logout_response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.logout_client()

        refresh_response = self.client.post(
            self.refresh_url,
            {
                "refresh": str(refresh),
            },
            format="json",
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_requires_refresh_field(self):
        self.authenticate_with_jwt(
            user=self.user
        )

        response = self.client.post(
            self.logout_url,
            {},
            format="json",
        )

        self.assert_validation_error(
            response,
            field="refresh",
        )

    def test_logout_rejects_invalid_refresh(self):
        self.authenticate_with_jwt(
            user=self.user
        )

        response = self.client.post(
            self.logout_url,
            {
                "refresh": "invalid-token",
            },
            format="json",
        )

        self.assert_validation_error(
            response,
            field="refresh",
        )


class CurrentUserApiTests(
    AccountApiBaseTestCase
):
    def test_me_requires_authentication(self):
        response = self.client.get(
            self.me_url
        )

        self.assert_authentication_required(
            response
        )

    def test_get_me_returns_current_user(self):
        self.authenticate_with_jwt(
            user=self.user
        )

        response = self.client.get(
            self.me_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.user.pk,
        )
        self.assertEqual(
            response.data["username"],
            self.user.username,
        )
        self.assertEqual(
            response.data["full_name"],
            self.user.full_name,
        )

    def test_patch_me_updates_editable_fields(
        self,
    ):
        self.authenticate_with_jwt(
            user=self.user
        )

        response = self.client.patch(
            self.me_url,
            {
                "email": "updated@example.com",
                "first_name": "Пётр",
                "last_name": "Петров",
                "middle_name": "Петрович",
                "phone": "+998900000099",
                "interface_language": "uz",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.email,
            "updated@example.com",
        )
        self.assertEqual(
            self.user.first_name,
            "Пётр",
        )
        self.assertEqual(
            self.user.last_name,
            "Петров",
        )
        self.assertEqual(
            self.user.middle_name,
            "Петрович",
        )
        self.assertEqual(
            self.user.phone,
            "+998900000099",
        )
        self.assertEqual(
            self.user.interface_language,
            "uz",
        )

    def test_patch_me_does_not_change_read_only_fields(
        self,
    ):
        original_username = self.user.username
        original_is_staff = self.user.is_staff
        original_is_active = self.user.is_active

        self.authenticate_with_jwt(
            user=self.user
        )

        response = self.client.patch(
            self.me_url,
            {
                "username": "hacked_username",
                "is_staff": True,
                "is_active": False,
                "must_change_password": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.username,
            original_username,
        )
        self.assertEqual(
            self.user.is_staff,
            original_is_staff,
        )
        self.assertEqual(
            self.user.is_active,
            original_is_active,
        )

    def test_patch_me_rejects_invalid_language(
        self,
    ):
        self.authenticate_with_jwt(
            user=self.user
        )

        response = self.client.patch(
            self.me_url,
            {
                "interface_language": "en",
            },
            format="json",
        )

        self.assert_validation_error(
            response,
            field="interface_language",
        )


class ChangePasswordApiTests(
    AccountApiBaseTestCase
):
    new_password = "New-account-password-456"

    def test_change_password_requires_authentication(
        self,
    ):
        response = self.client.post(
            self.change_password_url,
            {
                "current_password": (
                    self.password
                ),
                "new_password": (
                    self.new_password
                ),
                "new_password_confirmation": (
                    self.new_password
                ),
            },
            format="json",
        )

        self.assert_authentication_required(
            response
        )

    def test_change_password_success(self):
        self.authenticate_with_jwt(
            user=self.user
        )

        response = self.client.post(
            self.change_password_url,
            {
                "current_password": (
                    self.password
                ),
                "new_password": (
                    self.new_password
                ),
                "new_password_confirmation": (
                    self.new_password
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["detail"],
            "Пароль успешно изменён.",
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                self.new_password
            )
        )
        self.assertFalse(
            self.user.must_change_password
        )

    def test_old_password_no_longer_allows_login(
        self,
    ):
        self.authenticate_with_jwt(
            user=self.user
        )

        change_response = self.client.post(
            self.change_password_url,
            {
                "current_password": (
                    self.password
                ),
                "new_password": (
                    self.new_password
                ),
                "new_password_confirmation": (
                    self.new_password
                ),
            },
            format="json",
        )

        self.assertEqual(
            change_response.status_code,
            status.HTTP_200_OK,
        )

        self.logout_client()

        old_login_response = self.client.post(
            self.login_url,
            {
                "username": self.user.username,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            old_login_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        new_login_response = self.client.post(
            self.login_url,
            {
                "username": self.user.username,
                "password": self.new_password,
            },
            format="json",
        )

        self.assertEqual(
            new_login_response.status_code,
            status.HTTP_200_OK,
        )

    def test_wrong_current_password_is_rejected(
        self,
    ):
        self.authenticate_with_jwt(
            user=self.user
        )

        response = self.client.post(
            self.change_password_url,
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
            },
            format="json",
        )

        self.assert_validation_error(
            response,
            field="current_password",
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                self.password
            )
        )

    def test_password_mismatch_is_rejected(
        self,
    ):
        self.authenticate_with_jwt(
            user=self.user
        )

        response = self.client.post(
            self.change_password_url,
            {
                "current_password": (
                    self.password
                ),
                "new_password": (
                    self.new_password
                ),
                "new_password_confirmation": (
                    "Different-password-789"
                ),
            },
            format="json",
        )

        self.assert_validation_error(
            response,
            field=(
                "new_password_confirmation"
            ),
        )

    def test_weak_password_is_rejected(self):
        self.authenticate_with_jwt(
            user=self.user
        )

        response = self.client.post(
            self.change_password_url,
            {
                "current_password": (
                    self.password
                ),
                "new_password": "123",
                "new_password_confirmation": "123",
            },
            format="json",
        )

        self.assert_validation_error(
            response,
            field="new_password",
        )