from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common.api.mixins import (
    AuditedArchiveModelMixin,
)


class BaseArchiveModelViewSet(
    AuditedArchiveModelMixin,
    ModelViewSet,
):
    model = None

    def get_archived_queryset(self):
        return self.model.all_objects.archived()

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

    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
    )
    def restore(self, request, pk=None):
        instance = get_object_or_404(
            self.model.all_objects,
            pk=pk,
            is_archived=True,
        )

        self.check_object_permissions(
            request,
            instance,
        )

        instance.restore(user=request.user)

        serializer = self.get_serializer(instance)

        return Response(
            {
                "detail": "Запись восстановлена из архива.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )