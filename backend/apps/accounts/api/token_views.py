from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema,
)
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.accounts.api.serializers import (
    CustomTokenObtainPairSerializer,
    TokenRefreshRequestSerializer,
    TokenRefreshResponseSerializer,
    TokenResponseSerializer,
    TokenVerifyRequestSerializer,
    TokenVerifyResponseSerializer,
)
from apps.common.api.schema import (
    BAD_REQUEST_RESPONSE,
    UNAUTHORIZED_RESPONSE,
)


class CustomTokenObtainPairView(
    TokenObtainPairView
):
    """
    Получение access и refresh JWT-токенов.
    """

    permission_classes = [AllowAny]
    serializer_class = (
        CustomTokenObtainPairSerializer
    )

    @extend_schema(
        tags=["Аутентификация"],
        summary="Вход в систему",
        description=(
            "Проверяет имя пользователя и пароль, "
            "возвращает access-токен, refresh-токен "
            "и сведения о пользователе."
        ),
        request=CustomTokenObtainPairSerializer,
        responses={
            200: TokenResponseSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
        },
        examples=[
            OpenApiExample(
                name="Запрос входа",
                value={
                    "username": "admin",
                    "password": "password",
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Успешный вход",
                value={
                    "refresh": "jwt-refresh-token",
                    "access": "jwt-access-token",
                    "user": {
                        "id": 1,
                        "username": "admin",
                        "email": (
                            "admin@example.com"
                        ),
                        "first_name": "Администратор",
                        "last_name": "Системы",
                        "middle_name": "",
                        "full_name": (
                            "Системы Администратор"
                        ),
                        "phone": "",
                        "avatar": None,
                        "interface_language": "ru",
                        "must_change_password": False,
                        "is_active": True,
                        "is_staff": True,
                        "groups": [
                            "Администраторы"
                        ],
                        "permissions": [],
                        "last_login": None,
                        "created_at": (
                            "2026-07-30T10:00:00+05:00"
                        ),
                        "updated_at": (
                            "2026-07-30T10:00:00+05:00"
                        ),
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(
            request,
            *args,
            **kwargs,
        )


class CustomTokenRefreshView(
    TokenRefreshView
):
    """
    Обновление access-токена.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Аутентификация"],
        summary="Обновить JWT-токен",
        description=(
            "Принимает действующий refresh-токен "
            "и возвращает новый access-токен. "
            "При включённой ротации также возвращает "
            "новый refresh-токен."
        ),
        request=TokenRefreshRequestSerializer,
        responses={
            200: TokenRefreshResponseSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(
            request,
            *args,
            **kwargs,
        )

class CustomTokenVerifyView(
    TokenVerifyView
):
    """
    Проверка действительности JWT-токена.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Аутентификация"],
        summary="Проверить JWT-токен",
        description=(
            "Проверяет подпись и срок действия "
            "access или refresh JWT-токена."
        ),
        request=TokenVerifyRequestSerializer,
        responses={
            200: TokenVerifyResponseSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
        },
        examples=[
            OpenApiExample(
                name="Проверка токена",
                value={
                    "token": "jwt-token",
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Токен действителен",
                value={},
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def post(
        self,
        request,
        *args,
        **kwargs,
    ):
        return super().post(
            request,
            *args,
            **kwargs,
        )