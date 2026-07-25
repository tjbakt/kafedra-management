from django.db.models import Q
from django_filters import rest_framework as filters

from apps.staff.models import (
    AcademicDegree,
    AcademicTitle,
    StaffEmployment,
    StaffEmploymentAcademicYear,
    StaffMember,
    StaffPosition,
    WorkloadNorm,
)


class StaffPositionFilter(filters.FilterSet):
    category = filters.ChoiceFilter(
        choices=StaffPosition.Category.choices,
    )
    is_teaching_position = filters.BooleanFilter()
    is_active = filters.BooleanFilter()

    class Meta:
        model = StaffPosition
        fields = (
            "category",
            "is_teaching_position",
            "is_active",
        )


class AcademicDegreeFilter(filters.FilterSet):
    is_active = filters.BooleanFilter()

    class Meta:
        model = AcademicDegree
        fields = ("is_active",)


class AcademicTitleFilter(filters.FilterSet):
    is_active = filters.BooleanFilter()

    class Meta:
        model = AcademicTitle
        fields = ("is_active",)


class StaffMemberFilter(filters.FilterSet):
    query = filters.CharFilter(method="filter_query")
    department = filters.NumberFilter(
        field_name="employments__department_id",
    )
    faculty = filters.NumberFilter(
        field_name="employments__department__faculty_id",
    )
    position = filters.NumberFilter(
        field_name="employments__position_id",
    )
    academic_degree = filters.NumberFilter(
        field_name="academic_degree_id",
    )
    academic_title = filters.NumberFilter(
        field_name="academic_title_id",
    )
    has_academic_degree = filters.BooleanFilter(
        method="filter_has_degree",
    )
    has_academic_title = filters.BooleanFilter(
        method="filter_has_title",
    )
    is_active = filters.BooleanFilter()

    def filter_query(self, queryset, name, value):
        value = value.strip()

        if not value:
            return queryset

        return queryset.filter(
            Q(personnel_number__icontains=value)
            | Q(last_name__icontains=value)
            | Q(first_name__icontains=value)
            | Q(middle_name__icontains=value)
            | Q(phone__icontains=value)
            | Q(email__icontains=value)
        )

    def filter_has_degree(self, queryset, name, value):
        if value:
            return queryset.filter(
                academic_degree__isnull=False
            )

        return queryset.filter(
            academic_degree__isnull=True
        )

    def filter_has_title(self, queryset, name, value):
        if value:
            return queryset.filter(
                academic_title__isnull=False
            )

        return queryset.filter(
            academic_title__isnull=True
        )

    class Meta:
        model = StaffMember
        fields = (
            "department",
            "faculty",
            "position",
            "academic_degree",
            "academic_title",
            "has_academic_degree",
            "has_academic_title",
            "is_active",
        )


class StaffEmploymentFilter(filters.FilterSet):
    staff_member = filters.NumberFilter(
        field_name="staff_member_id",
    )
    university = filters.NumberFilter(
        field_name="department__faculty__university_id",
    )
    faculty = filters.NumberFilter(
        field_name="department__faculty_id",
    )
    department = filters.NumberFilter(
        field_name="department_id",
    )
    position = filters.NumberFilter(
        field_name="position_id",
    )
    employment_type = filters.ChoiceFilter(
        choices=StaffEmployment.EmploymentType.choices,
    )
    rate = filters.NumberFilter()
    is_primary = filters.BooleanFilter()
    is_active = filters.BooleanFilter()

    class Meta:
        model = StaffEmployment
        fields = (
            "staff_member",
            "university",
            "faculty",
            "department",
            "position",
            "employment_type",
            "rate",
            "is_primary",
            "is_active",
        )

class StaffEmploymentAcademicYearFilter(
    filters.FilterSet
):
    academic_year = filters.NumberFilter(
        field_name="academic_year_id",
    )
    staff_employment = filters.NumberFilter(
        field_name="staff_employment_id",
    )
    staff_member = filters.NumberFilter(
        field_name="staff_employment__staff_member_id",
    )
    university = filters.NumberFilter(
        field_name=(
            "staff_employment__department__faculty__"
            "university_id"
        ),
    )
    faculty = filters.NumberFilter(
        field_name=(
            "staff_employment__department__faculty_id"
        ),
    )
    department = filters.NumberFilter(
        field_name="staff_employment__department_id",
    )
    position = filters.NumberFilter(
        field_name="staff_employment__position_id",
    )
    rate = filters.NumberFilter()
    academic_degree = filters.NumberFilter(
        field_name="academic_degree_id",
    )
    academic_title = filters.NumberFilter(
        field_name="academic_title_id",
    )
    has_academic_degree = filters.BooleanFilter(
        method="filter_has_academic_degree",
    )
    has_academic_title = filters.BooleanFilter(
        method="filter_has_academic_title",
    )
    is_active = filters.BooleanFilter()

    def filter_has_academic_degree(
        self,
        queryset,
        name,
        value,
    ):
        return queryset.filter(
            academic_degree__isnull=not value
        )

    def filter_has_academic_title(
        self,
        queryset,
        name,
        value,
    ):
        return queryset.filter(
            academic_title__isnull=not value
        )

    class Meta:
        model = StaffEmploymentAcademicYear
        fields = (
            "academic_year",
            "staff_employment",
            "staff_member",
            "university",
            "faculty",
            "department",
            "position",
            "rate",
            "academic_degree",
            "academic_title",
            "has_academic_degree",
            "has_academic_title",
            "is_active",
        )

class WorkloadNormFilter(filters.FilterSet):
    academic_year = filters.NumberFilter(
        field_name="academic_year_id",
    )
    rate = filters.NumberFilter()
    has_academic_degree = filters.BooleanFilter()
    has_academic_title = filters.BooleanFilter()
    is_active = filters.BooleanFilter()

    class Meta:
        model = WorkloadNorm
        fields = (
            "academic_year",
            "rate",
            "has_academic_degree",
            "has_academic_title",
            "is_active",
        )