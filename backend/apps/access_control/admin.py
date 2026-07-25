from django.contrib import admin

from apps.access_control.models import (
    SystemRole,
    UserRoleAssignment,
)


class ArchiveAdminMixin:
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "is_archived",
        "archived_at",
        "archived_by",
    )

    def get_queryset(self, request):
        return self.model.all_objects.all()


@admin.register(SystemRole)
class SystemRoleAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name_ru",
        "is_active",
        "sort_order",
        "is_archived",
    )
    list_filter = (
        "is_active",
        "is_archived",
    )
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
    )


@admin.register(UserRoleAssignment)
class UserRoleAssignmentAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "user",
        "role",
        "scope_type",
        "university",
        "faculty",
        "department",
        "staff_member",
        "valid_from",
        "valid_until",
        "is_active",
        "is_current",
    )
    list_filter = (
        "role",
        "scope_type",
        "university",
        "faculty",
        "department",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "role__name_ru",
        "department__name_ru",
        "faculty__name_ru",
        "staff_member__last_name",
        "staff_member__first_name",
        "staff_member__personnel_number",
    )
    autocomplete_fields = (
        "user",
        "role",
        "university",
        "faculty",
        "department",
        "staff_member",
    )