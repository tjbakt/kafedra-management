from rest_framework import status
from rest_framework.response import Response


class UserAuditMixin:
    """
    Автоматически заполняет created_by и updated_by.
    """

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user,
        )


class ArchiveModelMixin:
    """
    Вместо физического удаления архивирует объект.
    """

    archive_response_message = "Запись перемещена в архив."

    def perform_destroy(self, instance):
        instance.archive(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {
                "detail": self.archive_response_message,
            },
            status=status.HTTP_200_OK,
        )


class AuditedArchiveModelMixin(
    UserAuditMixin,
    ArchiveModelMixin,
):
    """
    Общий mixin для стандартных CRUD ViewSet.
    """