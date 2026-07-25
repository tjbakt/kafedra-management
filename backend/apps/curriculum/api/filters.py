from django.db.models import Q
from django_filters import rest_framework as filters

from apps.curriculum.models import (
    Curriculum,
    CurriculumDiscipline,
    CurriculumWorkload,
    Discipline,
    WorkloadType,
)


class DisciplineFilter(filters.FilterSet):
    query = filters.CharFilter(method="filter_query")
    default_department = filters.NumberFilter(
        field_name="default_department_id",
    )
    faculty = filters.NumberFilter(
        field_name="default_department__faculty_id",
    )
    is_active = filters.BooleanFilter()

    def filter_query(self, queryset, name, value):
        return queryset.filter(
            Q(code__icontains=value)
            | Q(name_ru__icontains=value)
            | Q(name_uz__icontains=value)
        )

    class Meta:
        model = Discipline
        fields = (
            "default_department",
            "faculty",
            "is_active",
        )


class WorkloadTypeFilter(filters.FilterSet):
    calculation_mode = filters.ChoiceFilter(
        choices=WorkloadType.CalculationMode.choices,
    )
    is_classroom = filters.BooleanFilter()
    is_teaching_load = filters.BooleanFilter()
    is_active = filters.BooleanFilter()

    class Meta:
        model = WorkloadType
        fields = (
            "calculation_mode",
            "is_classroom",
            "is_teaching_load",
            "is_active",
        )


class CurriculumFilter(filters.FilterSet):
    query = filters.CharFilter(method="filter_query")
    university = filters.NumberFilter(
        field_name="study_program__university_id",
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
    effective_academic_year = filters.NumberFilter(
        field_name="effective_academic_year_id",
    )
    status = filters.ChoiceFilter(
        choices=Curriculum.Status.choices,
    )
    is_active = filters.BooleanFilter()

    def filter_query(self, queryset, name, value):
        return queryset.filter(
            Q(code__icontains=value)
            | Q(study_program__code__icontains=value)
            | Q(study_program__name_ru__icontains=value)
            | Q(study_program__name_uz__icontains=value)
        )

    class Meta:
        model = Curriculum
        fields = (
            "university",
            "study_program",
            "education_level",
            "study_form",
            "effective_academic_year",
            "status",
            "is_active",
        )


class CurriculumDisciplineFilter(filters.FilterSet):
    curriculum = filters.NumberFilter(
        field_name="curriculum_id",
    )
    discipline = filters.NumberFilter(
        field_name="discipline_id",
    )
    semester_number = filters.NumberFilter()
    season = filters.CharFilter(method="filter_season")
    teaching_department = filters.NumberFilter(
        field_name="teaching_department_id",
    )
    faculty = filters.NumberFilter(
        field_name="teaching_department__faculty_id",
    )
    control_form = filters.ChoiceFilter(
        choices=CurriculumDiscipline.ControlForm.choices,
    )
    component_type = filters.ChoiceFilter(
        choices=CurriculumDiscipline.ComponentType.choices,
    )
    is_active = filters.BooleanFilter()

    def filter_season(self, queryset, name, value):
        if value == "autumn":
            return queryset.filter(semester_number__in=(1, 3, 5, 7, 9))

        if value == "spring":
            return queryset.filter(semester_number__in=(2, 4, 6, 8, 10))

        return queryset.none()

    class Meta:
        model = CurriculumDiscipline
        fields = (
            "curriculum",
            "discipline",
            "semester_number",
            "teaching_department",
            "faculty",
            "control_form",
            "component_type",
            "is_active",
        )


class CurriculumWorkloadFilter(filters.FilterSet):
    curriculum_discipline = filters.NumberFilter(
        field_name="curriculum_discipline_id",
    )
    curriculum = filters.NumberFilter(
        field_name="curriculum_discipline__curriculum_id",
    )
    workload_type = filters.NumberFilter(
        field_name="workload_type_id",
    )
    calculation_mode = filters.ChoiceFilter(
        choices=WorkloadType.CalculationMode.choices,
    )
    is_active = filters.BooleanFilter()

    class Meta:
        model = CurriculumWorkload
        fields = (
            "curriculum_discipline",
            "curriculum",
            "workload_type",
            "calculation_mode",
            "is_active",
        )