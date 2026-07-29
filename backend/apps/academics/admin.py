from django.contrib import admin

from apps.academics.models import (
    AcademicSemester,
    AcademicYear,
    EducationDuration,
    EducationLevel,
    StudentGroup,
    StudyForm,
    StudyProgram,
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


@admin.register(AcademicYear)
class AcademicYearAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "name",
        "status",
        "is_current",
        "is_active",
        "closed_at",
        "closed_by",
        "is_archived",
        "start_year",
        "end_year",
    )
    list_filter = (
        "status",
        "is_current",
        "is_active",
        "is_archived",
    )
    readonly_fields = (
        "status",
        "closed_at",
        "closed_by",
        "closing_comment",
        "reopened_at",
        "reopened_by",
        "reopening_reason",
    )
    ordering = ("-start_year",)
    search_fields = ("name", "start_year", "end_year")


@admin.register(EducationLevel)
class EducationLevelAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name_ru",
        "name_uz",
        "is_active",
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


@admin.register(StudyForm)
class StudyFormAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name_ru",
        "name_uz",
        "is_active",
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


@admin.register(EducationDuration)
class EducationDurationAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "education_level",
        "study_form",
        "duration_months",
        "semesters_count",
        "is_active",
    )
    list_filter = (
        "education_level",
        "study_form",
        "is_active",
        "is_archived",
    )
    autocomplete_fields = (
        "education_level",
        "study_form",
    )


@admin.register(AcademicSemester)
class AcademicSemesterAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "academic_year",
        "season",
        "start_date",
        "end_date",
        "is_current",
    )
    list_filter = (
        "season",
        "is_current",
        "is_active",
        "is_archived",
    )
    autocomplete_fields = ("academic_year",)

    search_fields = ("academic_year__name", "season", "start_date", "end_date")


@admin.register(StudyProgram)
class StudyProgramAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name_ru",
        "education_level",
        "profiling_department",
        "is_active",
    )
    list_filter = (
        "university",
        "education_level",
        "profiling_department__faculty",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
        "profiling_department__name_ru",
    )
    autocomplete_fields = (
        "university",
        "education_level",
        "profiling_department",
    )


@admin.register(StudentGroup)
class StudentGroupAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "faculty",
        "study_program",
        "study_form",
        "student_count",
        "is_active",
    )
    list_filter = (
        "faculty__university",
        "faculty",
        "study_program__education_level",
        "study_form",
        "academic_year_admission",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "code",
        "study_program__name_ru",
        "study_program__name_uz",
    )
    autocomplete_fields = (
        "academic_year_admission",
        "graduation_academic_year",
        "faculty",
        "study_program",
        "study_form",
    )