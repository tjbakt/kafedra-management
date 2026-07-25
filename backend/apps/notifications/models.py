from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """
    Информационное уведомление конкретному пользователю.
    """

    class Type(models.TextChoices):
        INFO = "info", _("Информация")
        SUCCESS = "success", _("Успешное действие")
        WARNING = "warning", _("Предупреждение")
        ERROR = "error", _("Ошибка")
        REMINDER = "reminder", _("Напоминание")
        ACTION_REQUIRED = (
            "action_required",
            _("Требуется действие"),
        )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Получатель"),
        related_name="notifications",
        on_delete=models.CASCADE,
    )
    notification_type = models.CharField(
        _("Тип"),
        max_length=30,
        choices=Type.choices,
        default=Type.INFO,
        db_index=True,
    )
    title = models.CharField(
        _("Заголовок"),
        max_length=500,
    )
    message = models.TextField(
        _("Сообщение"),
    )

    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_("Тип связанного объекта"),
        related_name="notifications",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    object_id = models.CharField(
        _("ID связанного объекта"),
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
    )
    content_object = GenericForeignKey(
        "content_type",
        "object_id",
    )
    object_repr = models.CharField(
        _("Представление объекта"),
        max_length=1000,
        blank=True,
    )

    action_url = models.CharField(
        _("Ссылка на действие"),
        max_length=2000,
        blank=True,
        help_text=_(
            "Внутренний маршрут frontend, например "
            "/individual-plans/15."
        ),
    )

    metadata = models.JSONField(
        _("Дополнительные данные"),
        default=dict,
        blank=True,
    )

    is_read = models.BooleanField(
        _("Прочитано"),
        default=False,
        db_index=True,
    )
    read_at = models.DateTimeField(
        _("Дата прочтения"),
        null=True,
        blank=True,
    )

    is_archived = models.BooleanField(
        _("Архивировано"),
        default=False,
        db_index=True,
    )
    archived_at = models.DateTimeField(
        _("Дата архивирования"),
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = _("Уведомление")
        verbose_name_plural = _("Уведомления")
        ordering = ("-created_at", "-id")
        indexes = [
            models.Index(
                fields=(
                    "recipient",
                    "is_read",
                    "-created_at",
                ),
                name="notification_recipient_idx",
            ),
            models.Index(
                fields=(
                    "content_type",
                    "object_id",
                ),
                name="notification_object_idx",
            ),
        ]

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(
                update_fields=(
                    "is_read",
                    "read_at",
                )
            )

    def archive(self):
        if not self.is_archived:
            self.is_archived = True
            self.archived_at = timezone.now()
            self.save(
                update_fields=(
                    "is_archived",
                    "archived_at",
                )
            )

    def __str__(self):
        return f"{self.recipient}: {self.title}"

class UserTask(models.Model):
    """
    Действие, которое пользователь должен выполнить.

    В отличие от Notification, задача имеет статус,
    срок и может быть назначена ответственному пользователю.
    """

    class Type(models.TextChoices):
        APPROVE_INDIVIDUAL_PLAN = (
            "approve_individual_plan",
            _("Утвердить индивидуальный план"),
        )
        REVIEW_INDIVIDUAL_PLAN = (
            "review_individual_plan",
            _("Проверить индивидуальный план"),
        )
        CONFIRM_PLAN_ITEM = (
            "confirm_plan_item",
            _("Подтвердить выполнение пункта плана"),
        )
        DISTRIBUTE_WORKLOAD = (
            "distribute_workload",
            _("Распределить учебную нагрузку"),
        )
        APPROVE_WORKLOAD = (
            "approve_workload",
            _("Утвердить распределение нагрузки"),
        )
        UPDATE_PLAN = (
            "update_plan",
            _("Доработать индивидуальный план"),
        )
        DEADLINE_REMINDER = (
            "deadline_reminder",
            _("Напоминание о сроке"),
        )
        OTHER = "other", _("Другая задача")

    class Status(models.TextChoices):
        OPEN = "open", _("Открыта")
        IN_PROGRESS = "in_progress", _("Выполняется")
        COMPLETED = "completed", _("Выполнена")
        CANCELLED = "cancelled", _("Отменена")
        EXPIRED = "expired", _("Просрочена")

    class Priority(models.TextChoices):
        LOW = "low", _("Низкий")
        NORMAL = "normal", _("Обычный")
        HIGH = "high", _("Высокий")
        URGENT = "urgent", _("Срочный")

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Ответственный"),
        related_name="assigned_tasks",
        on_delete=models.CASCADE,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Создал"),
        related_name="created_user_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    task_type = models.CharField(
        _("Тип задачи"),
        max_length=50,
        choices=Type.choices,
        default=Type.OTHER,
        db_index=True,
    )
    status = models.CharField(
        _("Статус"),
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    priority = models.CharField(
        _("Приоритет"),
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
        db_index=True,
    )

    title = models.CharField(
        _("Название"),
        max_length=500,
    )
    description = models.TextField(
        _("Описание"),
        blank=True,
    )

    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_("Тип связанного объекта"),
        related_name="user_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    object_id = models.CharField(
        _("ID связанного объекта"),
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
    )
    content_object = GenericForeignKey(
        "content_type",
        "object_id",
    )
    object_repr = models.CharField(
        _("Представление объекта"),
        max_length=1000,
        blank=True,
    )

    action_url = models.CharField(
        _("Ссылка на действие"),
        max_length=2000,
        blank=True,
    )

    due_date = models.DateField(
        _("Срок выполнения"),
        null=True,
        blank=True,
        db_index=True,
    )
    started_at = models.DateTimeField(
        _("Дата начала"),
        null=True,
        blank=True,
    )
    completed_at = models.DateTimeField(
        _("Дата выполнения"),
        null=True,
        blank=True,
    )
    cancelled_at = models.DateTimeField(
        _("Дата отмены"),
        null=True,
        blank=True,
    )

    completion_comment = models.TextField(
        _("Комментарий о выполнении"),
        blank=True,
    )
    cancellation_reason = models.TextField(
        _("Причина отмены"),
        blank=True,
    )

    deduplication_key = models.CharField(
        _("Ключ уникальности"),
        max_length=255,
        blank=True,
        db_index=True,
        help_text=_(
            "Используется для предотвращения повторного "
            "создания одинаковых открытых задач."
        ),
    )

    metadata = models.JSONField(
        _("Дополнительные данные"),
        default=dict,
        blank=True,
    )

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
        verbose_name = _("Задача пользователя")
        verbose_name_plural = _("Задачи пользователей")
        ordering = (
            "due_date",
            "-priority",
            "-created_at",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "assignee",
                    "deduplication_key",
                ),
                condition=Q(
                    deduplication_key__gt="",
                    status__in=(
                        "open",
                        "in_progress",
                    ),
                ),
                name="unique_open_task_deduplication",
            ),
        ]
        indexes = [
            models.Index(
                fields=(
                    "assignee",
                    "status",
                    "due_date",
                ),
                name="user_task_assignee_idx",
            ),
            models.Index(
                fields=(
                    "content_type",
                    "object_id",
                ),
                name="user_task_object_idx",
            ),
        ]

    @property
    def is_overdue(self):
        if not self.due_date:
            return False

        if self.status not in (
            self.Status.OPEN,
            self.Status.IN_PROGRESS,
        ):
            return False

        return self.due_date < timezone.localdate()

    def __str__(self):
        return f"{self.assignee}: {self.title}"