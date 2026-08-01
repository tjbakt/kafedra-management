from django.db.models import Q
from django_filters import rest_framework as filters

from apps.organizations.models import (
    Department,
    Faculty,
    University,
)


class OrganizationFilterMixin:
    """
    Общая логика текстовой фильтрации.

    Само декларативное поле query объявляется
    непосредственно в каждом FilterSet.
    """

    def filter_query(
        self,
        queryset,
        name,
        value,
    ):
        value = value.strip()

        if not value:
            return queryset

        return queryset.filter(
            Q(code__icontains=value)
            | Q(name_ru__icontains=value)
            | Q(name_uz__icontains=value)
            | Q(
                short_name_ru__icontains=value
            )
            | Q(
                short_name_uz__icontains=value
            )
        )


class UniversityFilter(
    OrganizationFilterMixin,
    filters.FilterSet,
):
    query = filters.CharFilter(
        method="filter_query",
        label="Поиск",
        help_text=(
            "Поиск по коду, полному "
            "и сокращённому названию."
        ),
    )

    is_active = filters.BooleanFilter()

    class Meta:
        model = University
        fields = (
            "query",
            "is_active",
        )


class FacultyFilter(
    OrganizationFilterMixin,
    filters.FilterSet,
):
    query = filters.CharFilter(
        method="filter_query",
        label="Поиск",
        help_text=(
            "Поиск по коду, полному "
            "и сокращённому названию."
        ),
    )

    university = filters.NumberFilter(
        field_name="university_id",
        min_value=1,
    )

    faculty_type = filters.ChoiceFilter(
        choices=Faculty.FacultyType.choices,
    )

    is_active = filters.BooleanFilter()

    class Meta:
        model = Faculty
        fields = (
            "query",
            "university",
            "faculty_type",
            "is_active",
        )


class DepartmentFilter(
    OrganizationFilterMixin,
    filters.FilterSet,
):
    query = filters.CharFilter(
        method="filter_query",
        label="Поиск",
        help_text=(
            "Поиск по коду, полному "
            "и сокращённому названию."
        ),
    )

    university = filters.NumberFilter(
        field_name=(
            "faculty__university_id"
        ),
        min_value=1,
    )

    faculty = filters.NumberFilter(
        field_name="faculty_id",
        min_value=1,
    )

    is_active = filters.BooleanFilter()

    class Meta:
        model = Department
        fields = (
            "query",
            "university",
            "faculty",
            "is_active",
        )