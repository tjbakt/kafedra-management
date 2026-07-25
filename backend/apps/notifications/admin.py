from django.contrib import admin

from apps.notifications.models import (
    Notification,
    UserTask,
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "recipient",
        "notification_type",
        "title",
        "is_read",
        "is_archived",
    )
    list_filter = (
        "notification_type",
        "is_read",
        "is_archived",
        "created_at",
    )
    search_fields = (
        "recipient__username",
        "recipient__first_name",
        "recipient__last_name",
        "title",
        "message",
        "object_repr",
    )
    readonly_fields = (
        "recipient",
        "notification_type",
        "title",
        "message",
        "content_type",
        "object_id",
        "object_repr",
        "action_url",
        "metadata",
        "is_read",
        "read_at",
        "is_archived",
        "archived_at",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False


@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "assignee",
        "task_type",
        "status",
        "priority",
        "due_date",
        "is_overdue",
        "created_at",
    )
    list_filter = (
        "task_type",
        "status",
        "priority",
        "due_date",
        "created_at",
    )
    search_fields = (
        "assignee__username",
        "assignee__first_name",
        "assignee__last_name",
        "title",
        "description",
        "object_repr",
        "deduplication_key",
    )
    autocomplete_fields = (
        "assignee",
        "created_by",
    )
    readonly_fields = (
        "content_type",
        "object_id",
        "object_repr",
        "created_at",
        "updated_at",
    )