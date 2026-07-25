from django.contrib import admin

from apps.organizations.models import (
    Department,
    Faculty,
    University,
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


@admin.register(University)
class UniversityAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name_ru",
        "name_uz",
        "is_active",
        "is_archived",
        "sort_order",
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
    ordering = (
        "sort_order",
        "name_ru",
    )


@admin.register(Faculty)
class FacultyAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name_ru",
        "faculty_type",
        "university",
        "is_active",
        "is_archived",
    )
    list_filter = (
        "university",
        "faculty_type",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
        "university__name_ru",
    )
    autocomplete_fields = (
        "university",
    )


@admin.register(Department)
class DepartmentAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name_ru",
        "faculty",
        "is_active",
        "is_archived",
    )
    list_filter = (
        "faculty__university",
        "faculty",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
        "faculty__name_ru",
    )
    autocomplete_fields = (
        "faculty",
    )