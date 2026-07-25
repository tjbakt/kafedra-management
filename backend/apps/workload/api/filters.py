from django_filters import rest_framework as filters

from apps.workload.models import WorkloadDistribution


class WorkloadDistributionFilter(filters.FilterSet):
    academic_year = filters.NumberFilter(
        field_name=(
            "planned_workload__academic_year_id"
        ),
    )
    academic_semester = filters.NumberFilter(
        field_name=(
            "planned_workload__academic_semester_id"
        ),
    )
    teaching_department = filters.NumberFilter(
        field_name=(
            "planned_workload__teaching_department_id"
        ),
    )
    faculty = filters.NumberFilter(
        field_name=(
            "planned_workload__teaching_department__faculty_id"
        ),
    )
    planned_workload = filters.NumberFilter(
        field_name="planned_workload_id",
    )
    teaching_stream = filters.NumberFilter(
        field_name=(
            "planned_workload__teaching_stream_id"
        ),
    )
    discipline = filters.NumberFilter(
        field_name=(
            "planned_workload__teaching_stream__"
            "curriculum_discipline__discipline_id"
        ),
    )
    workload_type = filters.NumberFilter(
        field_name=(
            "planned_workload__curriculum_workload__"
            "workload_type_id"
        ),
    )
    staff_member = filters.NumberFilter(
        field_name=(
            "staff_employment__staff_member_id"
        ),
    )
    staff_employment = filters.NumberFilter(
        field_name="staff_employment_id",
    )
    position = filters.NumberFilter(
        field_name="staff_employment__position_id",
    )
    status = filters.ChoiceFilter(
        choices=WorkloadDistribution.Status.choices,
    )

    class Meta:
        model = WorkloadDistribution
        fields = (
            "academic_year",
            "academic_semester",
            "teaching_department",
            "faculty",
            "planned_workload",
            "teaching_stream",
            "discipline",
            "workload_type",
            "staff_member",
            "staff_employment",
            "position",
            "status",
        )