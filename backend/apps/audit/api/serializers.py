from rest_framework import serializers

from apps.audit.models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    action_name = serializers.CharField(
        source="get_action_display",
        read_only=True,
    )
    model = serializers.CharField(
        source="content_type.model",
        read_only=True,
    )
    app_label = serializers.CharField(
        source="content_type.app_label",
        read_only=True,
    )
    content_type_name = serializers.CharField(
        source="content_type.name",
        read_only=True,
    )

    class Meta:
        model = AuditEvent
        fields = (
            "id",
            "content_type",
            "app_label",
            "model",
            "content_type_name",
            "object_id",
            "object_repr",
            "action",
            "action_name",
            "action_label",
            "old_values",
            "new_values",
            "changed_fields",
            "reason",
            "metadata",
            "actor",
            "actor_username",
            "actor_full_name",
            "ip_address",
            "user_agent",
            "request_method",
            "request_path",
            "university_id",
            "faculty_id",
            "department_id",
            "staff_member_id",
            "academic_year_id",
            "created_at",
        )
        read_only_fields = fields