from django.contrib import admin

from apps.curriculum.models import (
    Curriculum,
    CurriculumDiscipline,
    CurriculumWorkload,
    Discipline,
    WorkloadType,
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


@admin.register(Discipline)
class DisciplineAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name_ru",
        "default_department",
        "is_active",
        "is_archived",
    )
    list_filter = (
        "default_department__faculty",
        "default_department",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
    )
    autocomplete_fields = (
        "default_department",
    )


@admin.register(WorkloadType)
class WorkloadTypeAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name_ru",
        "calculation_mode",
        "is_classroom",
        "is_teaching_load",
        "is_active",
    )
    list_filter = (
        "calculation_mode",
        "is_classroom",
        "is_teaching_load",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
    )


@admin.register(Curriculum)
class CurriculumAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "study_program",
        "study_form",
        "effective_academic_year",
        "version",
        "status",
        "is_active",
    )
    list_filter = (
        "study_program__education_level",
        "study_form",
        "effective_academic_year",
        "status",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "code",
        "study_program__code",
        "study_program__name_ru",
        "study_program__name_uz",
    )
    autocomplete_fields = (
        "study_program",
        "study_form",
        "effective_academic_year",
    )


@admin.register(CurriculumDiscipline)
class CurriculumDisciplineAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "discipline",
        "curriculum",
        "semester_number",
        "teaching_department",
        "control_form",
        "credits",
        "is_active",
    )
    list_filter = (
        "curriculum",
        "semester_number",
        "teaching_department__faculty",
        "teaching_department",
        "control_form",
        "component_type",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "discipline__code",
        "discipline__name_ru",
        "discipline__name_uz",
        "curriculum__code",
        "teaching_department__name_ru",
        "teaching_department__name_uz",
    )
    autocomplete_fields = (
        "curriculum",
        "discipline",
        "teaching_department",
    )


@admin.register(CurriculumWorkload)
class CurriculumWorkloadAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "curriculum_discipline",
        "workload_type",
        "calculation_mode",
        "base_hours",
        "is_active",
    )
    list_filter = (
        "workload_type",
        "calculation_mode",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "curriculum_discipline__discipline__code",
        "curriculum_discipline__discipline__name_ru",
        "curriculum_discipline__curriculum__code",
        "workload_type__name_ru",
        "workload_type__name_uz",
    )
    autocomplete_fields = (
        "curriculum_discipline",
        "workload_type",
    )