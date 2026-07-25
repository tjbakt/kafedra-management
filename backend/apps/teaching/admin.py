from django.contrib import admin

from apps.teaching.models import (
    GroupCurriculumAssignment,
    GroupSemester,
    PlannedWorkload,
    TeachingStream,
    TeachingStreamGroup,
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


@admin.register(GroupCurriculumAssignment)
class GroupCurriculumAssignmentAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "student_group",
        "curriculum",
        "start_academic_year",
        "is_primary",
        "is_active",
        "is_archived",
    )
    list_filter = (
        "curriculum__study_program",
        "curriculum__study_form",
        "start_academic_year",
        "is_primary",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "student_group__code",
        "curriculum__code",
    )
    autocomplete_fields = (
        "student_group",
        "curriculum",
        "start_academic_year",
        "end_academic_year",
    )


@admin.register(GroupSemester)
class GroupSemesterAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "student_group",
        "academic_year",
        "semester_number",
        "students_count",
        "subgroup_count",
        "status",
    )
    list_filter = (
        "academic_year",
        "academic_semester",
        "semester_number",
        "status",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "group_curriculum__student_group__code",
    )
    autocomplete_fields = (
        "group_curriculum",
        "academic_year",
        "academic_semester",
    )


class TeachingStreamGroupInline(admin.TabularInline):
    model = TeachingStreamGroup
    extra = 0
    autocomplete_fields = ("group_semester",)


@admin.register(TeachingStream)
class TeachingStreamAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name",
        "academic_year",
        "academic_semester",
        "workload_type",
        "teaching_department",
        "status",
    )
    list_filter = (
        "academic_year",
        "academic_semester",
        "teaching_department",
        "curriculum_workload__workload_type",
        "status",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "code",
        "name",
        "curriculum_discipline__discipline__name_ru",
    )
    autocomplete_fields = (
        "academic_year",
        "academic_semester",
        "curriculum_discipline",
        "curriculum_workload",
        "teaching_department",
    )
    inlines = (TeachingStreamGroupInline,)


@admin.register(TeachingStreamGroup)
class TeachingStreamGroupAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "teaching_stream",
        "group_semester",
        "is_active",
        "is_archived",
    )
    autocomplete_fields = (
        "teaching_stream",
        "group_semester",
    )


@admin.register(PlannedWorkload)
class PlannedWorkloadAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "teaching_stream",
        "teaching_department",
        "calculation_mode",
        "base_hours",
        "calculation_quantity",
        "total_hours",
        "status",
    )
    list_filter = (
        "academic_year",
        "academic_semester",
        "teaching_department",
        "curriculum_workload__workload_type",
        "status",
        "is_archived",
    )
    search_fields = (
        "teaching_stream__code",
        "teaching_stream__name",
        "teaching_stream__curriculum_discipline__"
        "discipline__name_ru",
    )
    readonly_fields = (
        *ArchiveAdminMixin.readonly_fields,
        "academic_year",
        "academic_semester",
        "teaching_department",
        "curriculum_workload",
        "calculation_mode",
        "base_hours",
        "calculation_quantity",
        "total_hours",
        "groups_count",
        "subgroups_count",
        "students_count",
        "calculated_at",
    )