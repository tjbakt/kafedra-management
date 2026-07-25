from django.db import models
from django.utils import timezone


class ArchiveQuerySet(models.QuerySet):
    """
    QuerySet с поддержкой мягкого архивирования.
    """

    def active(self):
        return self.filter(is_archived=False)

    def archived(self):
        return self.filter(is_archived=True)

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


class ActiveManager(models.Manager):
    """
    Менеджер по умолчанию.

    Возвращает только неархивированные записи.
    """

    def get_queryset(self):
        return ArchiveQuerySet(
            self.model,
            using=self._db,
        ).filter(is_archived=False)


class AllObjectsManager(models.Manager):
    """
    Возвращает все записи, включая архивные.
    """

    def get_queryset(self):
        return ArchiveQuerySet(
            self.model,
            using=self._db,
        )