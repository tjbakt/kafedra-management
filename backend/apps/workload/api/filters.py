from django_filters import rest_framework as filters

from apps.workload.models import WorkloadDistribution


class WorkloadDistributionFilter(
    filters.FilterSet
):
    """
    Фильтры списка распределений учебной нагрузки.
    """

    academic_year = filters.NumberFilter(
        field_name=(
            "planned_workload__academic_year_id"
        ),
        min_value=1,
        label="Учебный год",
        help_text="Фильтр по ID учебного года.",
    )

    academic_semester = filters.NumberFilter(
        field_name=(
            "planned_workload__academic_semester_id"
        ),
        min_value=1,
        label="Семестр учебного года",
        help_text=(
            "Фильтр по ID семестра учебного года."
        ),
    )

    teaching_department = filters.NumberFilter(
        field_name=(
            "planned_workload__teaching_department_id"
        ),
        min_value=1,
        label="Кафедра нагрузки",
        help_text=(
            "Фильтр по ID кафедры, за которой "
            "закреплена плановая нагрузка."
        ),
    )

    faculty = filters.NumberFilter(
        field_name=(
            "planned_workload__teaching_department__"
            "faculty_id"
        ),
        min_value=1,
        label="Факультет",
        help_text="Фильтр по ID факультета.",
    )

    planned_workload = filters.NumberFilter(
        field_name="planned_workload_id",
        min_value=1,
        label="Плановая нагрузка",
        help_text=(
            "Фильтр по ID плановой учебной нагрузки."
        ),
    )

    teaching_stream = filters.NumberFilter(
        field_name=(
            "planned_workload__teaching_stream_id"
        ),
        min_value=1,
        label="Учебный поток",
        help_text="Фильтр по ID учебного потока.",
    )

    discipline = filters.NumberFilter(
        field_name=(
            "planned_workload__teaching_stream__"
            "curriculum_discipline__discipline_id"
        ),
        min_value=1,
        label="Дисциплина",
        help_text="Фильтр по ID дисциплины.",
    )

    workload_type = filters.NumberFilter(
        field_name=(
            "planned_workload__curriculum_workload__"
            "workload_type_id"
        ),
        min_value=1,
        label="Вид нагрузки",
        help_text="Фильтр по ID вида нагрузки.",
    )

    staff_member = filters.NumberFilter(
        field_name=(
            "staff_employment__staff_member_id"
        ),
        min_value=1,
        label="Преподаватель",
        help_text="Фильтр по ID преподавателя.",
    )

    staff_employment = filters.NumberFilter(
        field_name="staff_employment_id",
        min_value=1,
        label="Трудовое назначение",
        help_text=(
            "Фильтр по ID трудового назначения "
            "преподавателя."
        ),
    )

    position = filters.NumberFilter(
        field_name=(
            "staff_employment__position_id"
        ),
        min_value=1,
        label="Должность",
        help_text="Фильтр по ID должности.",
    )

    status = filters.ChoiceFilter(
        choices=WorkloadDistribution.Status.choices,
        label="Статус распределения",
        help_text=(
            "Фильтр по бизнес-статусу "
            "распределения."
        ),
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