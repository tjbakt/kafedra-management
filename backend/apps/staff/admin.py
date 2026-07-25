from django.contrib import admin

from apps.staff.models import (
    AcademicDegree,
    AcademicTitle,
    StaffEmployment,
    StaffMember,
    StaffPosition,
    WorkloadNorm,
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


@admin.register(StaffPosition)
class StaffPositionAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name_ru",
        "category",
        "is_teaching_position",
        "is_active",
        "is_archived",
    )
    list_filter = (
        "category",
        "is_teaching_position",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
    )


@admin.register(AcademicDegree)
class AcademicDegreeAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name_ru",
        "short_name_ru",
        "is_active",
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


@admin.register(AcademicTitle)
class AcademicTitleAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name_ru",
        "short_name_ru",
        "is_active",
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

class StaffEmploymentInline(admin.TabularInline):
    model = StaffEmployment
    extra = 0
    fields = (
        "department",
        "position",
        "employment_type",
        "rate",
        "start_date",
        "end_date",
        "is_primary",
        "is_active",
    )
    autocomplete_fields = (
        "department",
        "position",
    )


@admin.register(StaffMember)
class StaffMemberAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "personnel_number",
        "full_name",
        "academic_degree",
        "academic_title",
        "is_active",
        "is_archived",
    )
    list_filter = (
        "academic_degree",
        "academic_title",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "personnel_number",
        "last_name",
        "first_name",
        "middle_name",
        "phone",
        "email",
    )
    autocomplete_fields = (
        "user",
        "academic_degree",
        "academic_title",
    )
    inlines = (
        StaffEmploymentInline,
    )


@admin.register(StaffEmployment)
class StaffEmploymentAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "staff_member",
        "department",
        "position",
        "employment_type",
        "rate",
        "is_primary",
        "is_active",
    )
    list_filter = (
        "department__faculty",
        "department",
        "position",
        "employment_type",
        "rate",
        "is_primary",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "staff_member__personnel_number",
        "staff_member__last_name",
        "staff_member__first_name",
        "department__name_ru",
        "position__name_ru",
    )
    autocomplete_fields = (
        "staff_member",
        "department",
        "position",
    )


@admin.register(WorkloadNorm)
class WorkloadNormAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "academic_year",
        "rate",
        "has_academic_degree",
        "has_academic_title",
        "annual_hours",
        "is_active",
    )
    list_filter = (
        "academic_year",
        "rate",
        "has_academic_degree",
        "has_academic_title",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "academic_year__start_year",
        "academic_year__end_year",
    )
    autocomplete_fields = (
        "academic_year",
    )