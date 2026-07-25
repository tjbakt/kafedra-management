from django.db.models import Q
from django_filters import rest_framework as filters

from apps.academics.models import (
    AcademicSemester,
    AcademicYear,
    EducationDuration,
    EducationLevel,
    StudentGroup,
    StudyForm,
    StudyProgram,
)


class AcademicYearFilter(filters.FilterSet):
    is_current = filters.BooleanFilter()
    is_active = filters.BooleanFilter()
    start_year = filters.NumberFilter()

    class Meta:
        model = AcademicYear
        fields = (
            "start_year",
            "is_current",
            "is_active",
        )


class AcademicSemesterFilter(filters.FilterSet):
    academic_year = filters.NumberFilter(
        field_name="academic_year_id",
    )
    season = filters.ChoiceFilter(
        choices=AcademicSemester.Season.choices,
    )
    is_current = filters.BooleanFilter()
    is_active = filters.BooleanFilter()

    class Meta:
        model = AcademicSemester
        fields = (
            "academic_year",
            "season",
            "is_current",
            "is_active",
        )


class EducationDurationFilter(filters.FilterSet):
    education_level = filters.NumberFilter(
        field_name="education_level_id",
    )
    study_form = filters.NumberFilter(
        field_name="study_form_id",
    )
    is_active = filters.BooleanFilter()

    class Meta:
        model = EducationDuration
        fields = (
            "education_level",
            "study_form",
            "is_active",
        )


class StudyProgramFilter(filters.FilterSet):
    query = filters.CharFilter(method="filter_query")
    university = filters.NumberFilter(
        field_name="university_id",
    )
    education_level = filters.NumberFilter(
        field_name="education_level_id",
    )
    profiling_department = filters.NumberFilter(
        field_name="profiling_department_id",
    )
    profiling_faculty = filters.NumberFilter(
        field_name="profiling_department__faculty_id",
    )
    is_active = filters.BooleanFilter()

    def filter_query(self, queryset, name, value):
        value = value.strip()

        if not value:
            return queryset

        return queryset.filter(
            Q(code__icontains=value)
            | Q(name_ru__icontains=value)
            | Q(name_uz__icontains=value)
        )

    class Meta:
        model = StudyProgram
        fields = (
            "university",
            "education_level",
            "profiling_department",
            "profiling_faculty",
            "is_active",
        )


class StudentGroupFilter(filters.FilterSet):
    query = filters.CharFilter(method="filter_query")
    university = filters.NumberFilter(
        field_name="faculty__university_id",
    )
    faculty = filters.NumberFilter(
        field_name="faculty_id",
    )
    faculty_type = filters.CharFilter(
        field_name="faculty__faculty_type",
    )
    study_program = filters.NumberFilter(
        field_name="study_program_id",
    )
    education_level = filters.NumberFilter(
        field_name="study_program__education_level_id",
    )
    study_form = filters.NumberFilter(
        field_name="study_form_id",
    )
    profiling_department = filters.NumberFilter(
        field_name="study_program__profiling_department_id",
    )
    academic_year_admission = filters.NumberFilter(
        field_name="academic_year_admission_id",
    )
    is_active = filters.BooleanFilter()

    def filter_query(self, queryset, name, value):
        value = value.strip()

        if not value:
            return queryset

        return queryset.filter(
            Q(code__icontains=value)
            | Q(study_program__name_ru__icontains=value)
            | Q(study_program__name_uz__icontains=value)
        )

    class Meta:
        model = StudentGroup
        fields = (
            "university",
            "faculty",
            "faculty_type",
            "study_program",
            "education_level",
            "study_form",
            "profiling_department",
            "academic_year_admission",
            "is_active",
        )