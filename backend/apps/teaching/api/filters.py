from django_filters import rest_framework as filters

from decimal import Decimal

from django.db import models

from apps.teaching.models import (
    GroupCurriculumAssignment,
    GroupSemester,
    PlannedWorkload,
    TeachingStream,
    TeachingStreamGroup,
)


class GroupCurriculumAssignmentFilter(filters.FilterSet):
    student_group = filters.NumberFilter(
        field_name="student_group_id",
    )
    curriculum = filters.NumberFilter(
        field_name="curriculum_id",
    )
    start_academic_year = filters.NumberFilter(
        field_name="start_academic_year_id",
    )
    is_primary = filters.BooleanFilter()
    is_active = filters.BooleanFilter()

    class Meta:
        model = GroupCurriculumAssignment
        fields = (
            "student_group",
            "curriculum",
            "start_academic_year",
            "is_primary",
            "is_active",
        )


class GroupSemesterFilter(filters.FilterSet):
    student_group = filters.NumberFilter(
        field_name="group_curriculum__student_group_id",
    )
    curriculum = filters.NumberFilter(
        field_name="group_curriculum__curriculum_id",
    )
    academic_year = filters.NumberFilter(
        field_name="academic_year_id",
    )
    academic_semester = filters.NumberFilter(
        field_name="academic_semester_id",
    )
    semester_number = filters.NumberFilter()
    faculty = filters.NumberFilter(
        field_name=(
            "group_curriculum__student_group__faculty_id"
        ),
    )
    profiling_department = filters.NumberFilter(
        field_name=(
            "group_curriculum__student_group__"
            "study_program__profiling_department_id"
        ),
    )
    status = filters.ChoiceFilter(
        choices=GroupSemester.Status.choices,
    )
    is_active = filters.BooleanFilter()

    class Meta:
        model = GroupSemester
        fields = (
            "student_group",
            "curriculum",
            "academic_year",
            "academic_semester",
            "semester_number",
            "faculty",
            "profiling_department",
            "status",
            "is_active",
        )


class TeachingStreamFilter(filters.FilterSet):
    academic_year = filters.NumberFilter(
        field_name="academic_year_id",
    )
    academic_semester = filters.NumberFilter(
        field_name="academic_semester_id",
    )
    curriculum = filters.NumberFilter(
        field_name=(
            "curriculum_discipline__curriculum_id"
        ),
    )
    curriculum_discipline = filters.NumberFilter(
        field_name="curriculum_discipline_id",
    )
    discipline = filters.NumberFilter(
        field_name=(
            "curriculum_discipline__discipline_id"
        ),
    )
    workload_type = filters.NumberFilter(
        field_name=(
            "curriculum_workload__workload_type_id"
        ),
    )
    teaching_department = filters.NumberFilter(
        field_name="teaching_department_id",
    )
    student_group = filters.NumberFilter(
        field_name=(
            "stream_groups__group_semester__"
            "group_curriculum__student_group_id"
        ),
    )
    status = filters.ChoiceFilter(
        choices=TeachingStream.Status.choices,
    )
    is_active = filters.BooleanFilter()

    class Meta:
        model = TeachingStream
        fields = (
            "academic_year",
            "academic_semester",
            "curriculum",
            "curriculum_discipline",
            "discipline",
            "workload_type",
            "teaching_department",
            "student_group",
            "status",
            "is_active",
        )


class TeachingStreamGroupFilter(filters.FilterSet):
    teaching_stream = filters.NumberFilter(
        field_name="teaching_stream_id",
    )
    group_semester = filters.NumberFilter(
        field_name="group_semester_id",
    )
    student_group = filters.NumberFilter(
        field_name=(
            "group_semester__group_curriculum__"
            "student_group_id"
        ),
    )
    is_active = filters.BooleanFilter()

    class Meta:
        model = TeachingStreamGroup
        fields = (
            "teaching_stream",
            "group_semester",
            "student_group",
            "is_active",
        )


class PlannedWorkloadFilter(filters.FilterSet):
    academic_year = filters.NumberFilter(
        field_name="academic_year_id",
    )
    academic_semester = filters.NumberFilter(
        field_name="academic_semester_id",
    )
    teaching_department = filters.NumberFilter(
        field_name="teaching_department_id",
    )
    discipline = filters.NumberFilter(
        field_name=(
            "teaching_stream__curriculum_discipline__"
            "discipline_id"
        ),
    )
    workload_type = filters.NumberFilter(
        field_name=(
            "curriculum_workload__workload_type_id"
        ),
    )
    status = filters.ChoiceFilter(
        choices=PlannedWorkload.Status.choices,
    )

    class Meta:
        model = PlannedWorkload
        fields = (
            "academic_year",
            "academic_semester",
            "teaching_department",
            "discipline",
            "workload_type",
            "status",
        )

    is_fully_distributed = filters.BooleanFilter(
        method="filter_fully_distributed",
    )

    def filter_fully_distributed(
        self,
        queryset,
        name,
        value,
    ):
        queryset = queryset.annotate(
            allocated_sum=models.Sum(
                "distributions__allocated_hours",
                filter=models.Q(
                    distributions__is_archived=False,
                    distributions__status__in=(
                        "draft",
                        "approved",
                    ),
                ),
            )
        ).annotate(
            effective_allocated=models.functions.Coalesce(
                "allocated_sum",
                models.Value(
                    Decimal("0.00"),
                    output_field=models.DecimalField(
                        max_digits=12,
                        decimal_places=2,
                    ),
                ),
            )
        )

        if value:
            return queryset.filter(
                effective_allocated__gte=models.F(
                    "total_hours"
                )
            )

        return queryset.filter(
            effective_allocated__lt=models.F(
                "total_hours"
            )
        )