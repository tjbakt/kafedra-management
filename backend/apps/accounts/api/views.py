from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

from apps.accounts.api.serializers import (
    ChangePasswordSerializer,
    LogoutSerializer,
    UserSerializer,
)

from apps.common.api.schema import (
    BAD_REQUEST_RESPONSE,
    DETAIL_RESPONSE,
    FORBIDDEN_RESPONSE,
    NO_CONTENT_RESPONSE,
    UNAUTHORIZED_RESPONSE,
)


@extend_schema_view(
    get=extend_schema(
        tags=["Аутентификация"],
        summary="Получить текущего пользователя",
        responses={
            200: UserSerializer,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
        },
    ),
    put=extend_schema(
        tags=["Аутентификация"],
        summary="Обновить профиль",
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
        },
    ),
    patch=extend_schema(
        tags=["Аутентификация"],
        summary="Частично обновить профиль",
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
        },
    ),
)
class CurrentUserAPIView(RetrieveUpdateAPIView):
    """
    Получение и изменение профиля текущего пользователя.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class LogoutAPIView(APIView):
    """
    Добавление refresh-токена в blacklist.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Аутентификация"],
        summary="Выход из системы",
        description=(
            "Добавляет refresh-токен в blacklist. "
        ),
        request=LogoutSerializer,
        responses={
            204: NO_CONTENT_RESPONSE,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
        },
    )
    def post(self, request):
        serializer = LogoutSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as exc:
            raise ValidationError(
                {
                    "refresh": [
                        (
                            "Refresh-токен недействителен или уже аннулирован."
                        )
                    ]
                }
            ) from exc

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class ChangePasswordAPIView(APIView):
    """
    Изменение пароля текущего пользователя.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Аутентификация"],
        summary="Изменить пароль",
        request=ChangePasswordSerializer,
        responses={
            200: DETAIL_RESPONSE,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
        },
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(
            serializer.validated_data["new_password"]
        )
        user.must_change_password = False
        user.save(
            update_fields=(
                "password",
                "must_change_password",
                "updated_at",
            )
        )

        return Response(
            {
                "detail": "Пароль успешно изменён."
            },
            status=status.HTTP_200_OK,
        )