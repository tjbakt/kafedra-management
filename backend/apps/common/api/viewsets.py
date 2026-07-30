from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common.api.mixins import (
    AuditedArchiveModelMixin,
)

from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from apps.common.api.schema import (
    BAD_REQUEST_RESPONSE,
    FORBIDDEN_RESPONSE,
    NOT_FOUND_RESPONSE,
    UNAUTHORIZED_RESPONSE,
)
from apps.common.api.schema_serializers import (
    RestoreResponseSerializer,
)


class BaseArchiveModelViewSet(
    AuditedArchiveModelMixin,
    ModelViewSet,
):
    """
    Базовый ViewSet для моделей с мягким удалением.

    Дочерний ViewSet должен определить:
    - model;
    - get_queryset();
    - при необходимости scope_queryset();
    - permission_classes.
    """

    model = None

    def scope_queryset(self, queryset):
        """
        Ограничивает queryset согласно области доступа
        текущего пользователя.

        По умолчанию ничего не ограничивает.
        Чувствительные ViewSet должны переопределить метод.
        """

        return queryset

    def get_archived_queryset(self):
        """
        Получает архивные записи и применяет к ним
        ту же область доступа, что и к активным данным.
        """

        if self.model is None:
            raise AssertionError(
                (
                    f"{self.__class__.__name__} должен "
                    "определить атрибут model."
                )
            )

        queryset = (
            self.model.all_objects
            .filter(is_archived=True)
        )

        return self.scope_queryset(queryset)

    @extend_schema(
        summary="Список архивных записей",
        description=(
            "Возвращает архивные записи "
            "текущего ресурса с учётом прав доступа, "
            "фильтрации, поиска и пагинации."
        ),
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                location=(
                    OpenApiParameter.QUERY
                ),
                required=False,
                description="Номер страницы.",
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=(
                    OpenApiParameter.QUERY
                ),
                required=False,
                description=(
                    "Размер страницы, максимум 100."
                ),
            ),
            OpenApiParameter(
                name="search",
                type=str,
                location=(
                    OpenApiParameter.QUERY
                ),
                required=False,
                description=(
                    "Поисковая строка, если ViewSet "
                    "поддерживает поиск."
                ),
            ),
            OpenApiParameter(
                name="ordering",
                type=str,
                location=(
                    OpenApiParameter.QUERY
                ),
                required=False,
                description=(
                    "Поле сортировки. Для обратной "
                    "сортировки используется префикс -."
                ),
            ),
        ],
        responses={
            200: OpenApiResponse(
                description=(
                    "Список архивных записей."
                ),
            ),
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="archived",
    )
    def archived(self, request):
        queryset = self.get_archived_queryset()
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )
            return self.get_paginated_response(
                serializer.data
            )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    @extend_schema(
        summary="Восстановить запись",
        description=(
                "Восстанавливает объект из архива. "
                "Операция может быть запрещена правами "
                "доступа или состоянием учебного года."
        ),
        request=None,
        responses={
            200: RestoreResponseSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
    )
    def restore(self, request, pk=None):
        queryset = self.get_archived_queryset()

        instance = get_object_or_404(
            queryset,
            pk=pk,
        )

        self.check_object_permissions(
            request,
            instance,
        )

        self.check_restore_permission(
            request,
            instance,
        )

        instance.restore(user=request.user)

        serializer = self.get_serializer(instance)

        return Response(
            {
                "detail": (
                    "Запись восстановлена из архива."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def check_restore_permission(
        self,
        request,
        instance,
    ):
        """
        Дополнительная точка проверки восстановления.

        Дочерний ViewSet может выбросить PermissionDenied.
        """

        return None