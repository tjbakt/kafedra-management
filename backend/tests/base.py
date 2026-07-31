from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import (
    RefreshToken,
)

from apps.access_control.models import (
    SystemRole,
)

from tests.factories.access_control import (
    UserRoleAssignmentFactory,
)
from tests.factories.accounts import (
    UserFactory,
)


User = get_user_model()


class BaseAPITestCase(APITestCase):
    """
    Базовый класс API-тестов проекта.
    """

    default_password = (
        "test-password-123"
    )

    def create_user(
        self,
        **kwargs,
    ):
        password = kwargs.pop(
            "password",
            self.default_password,
        )

        return UserFactory(
            password=password,
            **kwargs,
        )

    def create_global_admin(
        self,
        **kwargs,
    ):
        user = self.create_user(
            is_staff=True,
            **kwargs,
        )

        UserRoleAssignmentFactory.global_role(
            user=user,
            role_code=(
                SystemRole.Code.SYSTEM_ADMIN
            ),
        )

        return user

    def authenticate(
        self,
        user=None,
    ):
        user = (
            user
            or self.create_global_admin()
        )

        self.client.force_authenticate(
            user=user
        )

        return user

    def authenticate_with_jwt(
        self,
        user=None,
    ):
        user = (
            user
            or self.create_global_admin()
        )

        refresh = RefreshToken.for_user(
            user
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {refresh.access_token}"
            )
        )

        return user

    def logout_client(self):
        self.client.force_authenticate(
            user=None
        )
        self.client.credentials()