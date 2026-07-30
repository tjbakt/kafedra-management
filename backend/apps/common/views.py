from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


HealthCheckResponseSerializer = inline_serializer(
    name="HealthCheckResponse",
    fields={
        "status": serializers.CharField(),
        "service": serializers.CharField(),
        "api_version": serializers.CharField(),
    },
)


class HealthCheckAPIView(APIView):
    """
    Проверка работоспособности backend API.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Система"],
        summary="Проверить доступность API",
        description=(
                "Возвращает статус работоспособности backend-приложения."
        ),
        request=None,
        responses={
            200: HealthCheckResponseSerializer,
        },
        examples=[
            OpenApiExample(
                name="Сервис работает",
                value={
                    "status": "ok",
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "Управление учебным процессом",
                "api_version": "v1",
            },
        )