from rest_framework import serializers

from apps.notifications.models import (
    Notification,
    UserTask,
)
from drf_spectacular.utils import (
    extend_schema_field,
)


class NotificationSerializer(
    serializers.ModelSerializer
):
    notification_type_name = serializers.CharField(
        source="get_notification_type_display",
        read_only=True,
    )
    app_label = serializers.CharField(
        source="content_type.app_label",
        read_only=True,
        allow_null=True,
    )
    model = serializers.CharField(
        source="content_type.model",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Notification
        fields = (
            "id",
            "recipient",
            "notification_type",
            "notification_type_name",
            "title",
            "message",
            "content_type",
            "app_label",
            "model",
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
        read_only_fields = fields


class UserTaskSerializer(serializers.ModelSerializer):
    task_type_name = serializers.CharField(
        source="get_task_type_display",
        read_only=True,
    )
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    priority_name = serializers.CharField(
        source="get_priority_display",
        read_only=True,
    )
    assignee_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(
        read_only=True,
    )
    app_label = serializers.CharField(
        source="content_type.app_label",
        read_only=True,
        allow_null=True,
    )
    model = serializers.CharField(
        source="content_type.model",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = UserTask
        fields = (
            "id",
            "assignee",
            "assignee_name",
            "created_by",
            "created_by_name",
            "task_type",
            "task_type_name",
            "status",
            "status_name",
            "priority",
            "priority_name",
            "title",
            "description",
            "content_type",
            "app_label",
            "model",
            "object_id",
            "object_repr",
            "action_url",
            "due_date",
            "started_at",
            "completed_at",
            "cancelled_at",
            "completion_comment",
            "cancellation_reason",
            "metadata",
            "is_overdue",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    @extend_schema_field(
        serializers.CharField(
            allow_null=True,
        )
    )
    def get_assignee_name(self, obj) -> str | None:
        if not obj.assignee:
            return None
        return (
            obj.assignee.get_full_name()
            or obj.assignee.username
        )

    @extend_schema_field(
        serializers.CharField(
            allow_null=True,
        )
    )
    def get_created_by_name(self, obj) -> str | None:
        if not obj.created_by:
            return None

        return (
            obj.created_by.get_full_name()
            or obj.created_by.username
        )