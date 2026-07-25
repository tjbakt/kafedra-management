from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuditEvent(models.Model):
    """
    Неизменяемая запись бизнес-аудита.

    Записи не архивируются и не удаляются через обычный API.
    """

    class Action(models.TextChoices):
        CREATE = "create", _("Создание")
        UPDATE = "update", _("Изменение")
        STATUS_CHANGE = "status_change", _("Изменение статуса")
        SUBMIT = "submit", _("Отправка на рассмотрение")
        APPROVE = "approve", _("Утверждение")
        CONFIRM = "confirm", _("Подтверждение")
        RETURN = "return", _("Возврат на доработку")
        REJECT = "reject", _("Отклонение")
        CANCEL = "cancel", _("Отмена")
        COMPLETE = "complete", _("Выполнение")
        CALCULATE = "calculate", _("Расчёт")
        DISTRIBUTE = "distribute", _("Распределение")
        IMPORT = "import", _("Импорт")
        ARCHIVE = "archive", _("Архивирование")
        RESTORE = "restore", _("Восстановление")
        DELETE = "delete", _("Удаление")
        LOGIN = "login", _("Вход в систему")
        LOGOUT = "logout", _("Выход из системы")
        OTHER = "other", _("Другое действие")

    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_("Тип объекта"),
        related_name="audit_events",
        on_delete=models.PROTECT,
    )
    object_id = models.CharField(
        _("ID объекта"),
        max_length=100,
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

    action = models.CharField(
        _("Действие"),
        max_length=30,
        choices=Action.choices,
        db_index=True,
    )
    action_label = models.CharField(
        _("Описание действия"),
        max_length=500,
        blank=True,
    )

    old_values = models.JSONField(
        _("Старые значения"),
        default=dict,
        blank=True,
    )
    new_values = models.JSONField(
        _("Новые значения"),
        default=dict,
        blank=True,
    )
    changed_fields = models.JSONField(
        _("Изменённые поля"),
        default=list,
        blank=True,
    )
    metadata = models.JSONField(
        _("Дополнительные данные"),
        default=dict,
        blank=True,
    )

    reason = models.TextField(
        _("Причина или комментарий"),
        blank=True,
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Пользователь"),
        related_name="audit_events",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    actor_username = models.CharField(
        _("Имя пользователя"),
        max_length=255,
        blank=True,
    )
    actor_full_name = models.CharField(
        _("ФИО пользователя"),
        max_length=500,
        blank=True,
    )

    ip_address = models.GenericIPAddressField(
        _("IP-адрес"),
        null=True,
        blank=True,
    )
    user_agent = models.TextField(
        _("User-Agent"),
        blank=True,
    )
    request_method = models.CharField(
        _("HTTP-метод"),
        max_length=20,
        blank=True,
    )
    request_path = models.CharField(
        _("Путь запроса"),
        max_length=2000,
        blank=True,
    )

    university_id = models.PositiveBigIntegerField(
        _("ID университета"),
        null=True,
        blank=True,
        db_index=True,
    )
    faculty_id = models.PositiveBigIntegerField(
        _("ID факультета"),
        null=True,
        blank=True,
        db_index=True,
    )
    department_id = models.PositiveBigIntegerField(
        _("ID кафедры"),
        null=True,
        blank=True,
        db_index=True,
    )
    staff_member_id = models.PositiveBigIntegerField(
        _("ID сотрудника"),
        null=True,
        blank=True,
        db_index=True,
    )
    academic_year_id = models.PositiveBigIntegerField(
        _("ID учебного года"),
        null=True,
        blank=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        _("Дата и время"),
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = _("Событие аудита")
        verbose_name_plural = _("Журнал аудита")
        ordering = ("-created_at", "-id")
        indexes = [
            models.Index(
                fields=(
                    "content_type",
                    "object_id",
                    "-created_at",
                ),
                name="audit_object_history_idx",
            ),
            models.Index(
                fields=(
                    "actor",
                    "-created_at",
                ),
                name="audit_actor_history_idx",
            ),
            models.Index(
                fields=(
                    "action",
                    "-created_at",
                ),
                name="audit_action_history_idx",
            ),
            models.Index(
                fields=(
                    "department_id",
                    "-created_at",
                ),
                name="audit_department_idx",
            ),
            models.Index(
                fields=(
                    "staff_member_id",
                    "-created_at",
                ),
                name="audit_staff_member_idx",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            raise RuntimeError(
                "События аудита нельзя изменять после создания."
            )

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise RuntimeError(
            "События аудита нельзя удалять обычным способом."
        )

    def __str__(self):
        return (
            f"{self.get_action_display()}: "
            f"{self.object_repr or self.object_id}"
        )