from django_filters import rest_framework as filters

from apps.individual_plan.models import (
    IndividualActivityType,
    IndividualPlan,
    IndividualPlanItem,
    IndividualPlanSection,
)


class IndividualPlanSectionFilter(filters.FilterSet):
    is_active = filters.BooleanFilter()
    is_hourly = filters.BooleanFilter()

    class Meta:
        model = IndividualPlanSection
        fields = (
            "code",
            "is_active",
            "is_hourly",
        )


class IndividualActivityTypeFilter(filters.FilterSet):
    section = filters.NumberFilter(
        field_name="section_id",
    )
    is_active = filters.BooleanFilter()
    requires_evidence = filters.BooleanFilter()

    class Meta:
        model = IndividualActivityType
        fields = (
            "section",
            "is_active",
            "requires_evidence",
        )


class IndividualPlanFilter(filters.FilterSet):
    academic_year = filters.NumberFilter(
        field_name="academic_year_id",
    )
    staff_employment = filters.NumberFilter(
        field_name="staff_employment_id",
    )
    staff_member = filters.NumberFilter(
        field_name="staff_employment__staff_member_id",
    )
    department = filters.NumberFilter(
        field_name="staff_employment__department_id",
    )
    faculty = filters.NumberFilter(
        field_name="staff_employment__department__faculty_id",
    )
    status = filters.ChoiceFilter(
        choices=IndividualPlan.Status.choices,
    )

    class Meta:
        model = IndividualPlan
        fields = (
            "academic_year",
            "staff_employment",
            "staff_member",
            "department",
            "faculty",
            "status",
        )


class IndividualPlanItemFilter(filters.FilterSet):
    individual_plan = filters.NumberFilter(
        field_name="individual_plan_id",
    )
    academic_year = filters.NumberFilter(
        field_name="individual_plan__academic_year_id",
    )
    staff_member = filters.NumberFilter(
        field_name=(
            "individual_plan__staff_employment__staff_member_id"
        ),
    )
    section = filters.NumberFilter(
        field_name="section_id",
    )
    activity_type = filters.NumberFilter(
        field_name="activity_type_id",
    )
    academic_semester = filters.NumberFilter(
        field_name="academic_semester_id",
    )
    status = filters.ChoiceFilter(
        choices=IndividualPlanItem.Status.choices,
    )

    class Meta:
        model = IndividualPlanItem
        fields = (
            "individual_plan",
            "academic_year",
            "staff_member",
            "section",
            "activity_type",
            "academic_semester",
            "status",
        )