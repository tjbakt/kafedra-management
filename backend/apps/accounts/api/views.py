from rest_framework import status
from rest_framework.generics import (
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.api.serializers import (
    ChangePasswordSerializer,
    LogoutSerializer,
    UserSerializer,
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

    def post(self, request):
        serializer = LogoutSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {
                    "detail": (
                        "Refresh-токен недействителен "
                        "или уже аннулирован."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class ChangePasswordAPIView(APIView):
    """
    Изменение пароля текущего пользователя.
    """

    permission_classes = [IsAuthenticated]

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