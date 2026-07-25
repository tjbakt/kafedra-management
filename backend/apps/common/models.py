from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.managers import (
    ActiveManager,
    AllObjectsManager,
)


class TimeStampedModel(models.Model):
    """
    Добавляет дату создания и изменения записи.
    """

    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True,
        db_index=True,
    )
    updated_at = models.DateTimeField(
        _("Дата изменения"),
        auto_now=True,
    )

    class Meta:
        abstract = True


class UserTrackedModel(models.Model):
    """
    Хранит пользователей, создавших и изменивших запись.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Создал"),
        related_name="%(app_label)s_%(class)s_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Изменил"),
        related_name="%(app_label)s_%(class)s_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
    )

    class Meta:
        abstract = True


class ArchivableModel(models.Model):
    """
    Поддержка мягкого удаления через архивирование.
    """

    is_archived = models.BooleanField(
        _("В архиве"),
        default=False,
        db_index=True,
        editable=False,
    )
    archived_at = models.DateTimeField(
        _("Дата архивирования"),
        null=True,
        blank=True,
        editable=False,
    )
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Архивировал"),
        related_name="%(app_label)s_%(class)s_archived",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
    )

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def archive(self, user=None):
        if self.is_archived:
            return

        self.is_archived = True
        self.archived_at = timezone.now()
        self.archived_by = user

        self.save(
            update_fields=(
                "is_archived",
                "archived_at",
                "archived_by",
            )
        )

    def restore(self, user=None):
        if not self.is_archived:
            return

        self.is_archived = False
        self.archived_at = None
        self.archived_by = None

        update_fields = [
            "is_archived",
            "archived_at",
            "archived_by",
        ]

        if hasattr(self, "updated_by"):
            self.updated_by = user
            update_fields.append("updated_by")

        self.save(update_fields=update_fields)

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(
            using=using,
            keep_parents=keep_parents,
        )

    def delete(self, using=None, keep_parents=False):
        """
        Обычный delete не удаляет запись физически.
        """

        self.archive()


class BaseModel(
    TimeStampedModel,
    UserTrackedModel,
    ArchivableModel,
):
    """
    Основная базовая модель проекта.

    Большинство справочников и бизнес-сущностей должны
    наследоваться от этого класса.
    """

    class Meta:
        abstract = True