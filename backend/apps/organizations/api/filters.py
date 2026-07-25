from django.db.models import Q
from django_filters import rest_framework as filters

from apps.organizations.models import (
    Department,
    Faculty,
    University,
)


class OrganizationFilterMixin:
    query = filters.CharFilter(
        method="filter_query",
    )

    def filter_query(self, queryset, name, value):
        value = value.strip()

        if not value:
            return queryset

        return queryset.filter(
            Q(code__icontains=value)
            | Q(name_ru__icontains=value)
            | Q(name_uz__icontains=value)
            | Q(short_name_ru__icontains=value)
            | Q(short_name_uz__icontains=value)
        )


class UniversityFilter(
    OrganizationFilterMixin,
    filters.FilterSet,
):
    is_active = filters.BooleanFilter()

    class Meta:
        model = University
        fields = (
            "is_active",
        )


class FacultyFilter(
    OrganizationFilterMixin,
    filters.FilterSet,
):
    university = filters.NumberFilter(
        field_name="university_id",
    )
    faculty_type = filters.ChoiceFilter(
        choices=Faculty.FacultyType.choices,
    )
    is_active = filters.BooleanFilter()

    class Meta:
        model = Faculty
        fields = (
            "university",
            "faculty_type",
            "is_active",
        )


class DepartmentFilter(
    OrganizationFilterMixin,
    filters.FilterSet,
):
    university = filters.NumberFilter(
        field_name="faculty__university_id",
    )
    faculty = filters.NumberFilter(
        field_name="faculty_id",
    )
    is_active = filters.BooleanFilter()

    class Meta:
        model = Department
        fields = (
            "university",
            "faculty",
            "is_active",
        )