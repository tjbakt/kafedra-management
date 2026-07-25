from django.contrib import admin

from apps.audit.models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "action",
        "object_repr",
        "actor_username",
        "department_id",
        "staff_member_id",
    )
    list_filter = (
        "action",
        "content_type",
        "created_at",
    )
    search_fields = (
        "object_repr",
        "action_label",
        "reason",
        "actor_username",
        "actor_full_name",
        "object_id",
    )
    readonly_fields = (
        "content_type",
        "object_id",
        "object_repr",
        "action",
        "action_label",
        "old_values",
        "new_values",
        "changed_fields",
        "metadata",
        "reason",
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
    date_hierarchy = "created_at"

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