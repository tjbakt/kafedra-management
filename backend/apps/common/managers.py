from django.db import models
from django.utils import timezone


class ArchiveQuerySet(models.QuerySet):
    """
    QuerySet с поддержкой мягкого архивирования.
    """

    def active(self):
        return self.filter(
            is_archived=False,
        )

    def archived(self):
        return self.filter(
            is_archived=True,
        )

    def archive(self, user=None):
        return self.update(
            is_archived=True,
            archived_at=timezone.now(),
            archived_by=user,
        )

    def restore(self):
        return self.update(
            is_archived=False,
            archived_at=None,
            archived_by=None,
        )

    def hard_delete(self):
        return super().delete()


class ArchiveManager(
    models.Manager.from_queryset(
        ArchiveQuerySet
    )
):
    """
    Базовый manager, публикующий методы
    ArchiveQuerySet на уровне manager:

    Model.objects.active()
    Model.all_objects.archived()
    """

    pass


class ActiveManager(ArchiveManager):
    """
    Менеджер по умолчанию.

    Возвращает только неархивированные записи.
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .active()
        )


class AllObjectsManager(ArchiveManager):
    """
    Возвращает все записи, включая архивные.
    """

    def get_queryset(self):
        return super().get_queryset()