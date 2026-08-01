from django.test import SimpleTestCase

from apps.organizations.api.filters import (
    DepartmentFilter,
    FacultyFilter,
    UniversityFilter,
)


class OrganizationFilterDeclarationTests(
    SimpleTestCase
):
    def test_university_filter_contains_query(
        self,
    ):
        self.assertIn(
            "query",
            UniversityFilter.base_filters,
        )

    def test_faculty_filter_contains_query(
        self,
    ):
        self.assertIn(
            "query",
            FacultyFilter.base_filters,
        )

    def test_department_filter_contains_query(
        self,
    ):
        self.assertIn(
            "query",
            DepartmentFilter.base_filters,
        )

    def test_related_id_filters_have_min_value(
        self,
    ):
        self.assertEqual(
            FacultyFilter
            .base_filters["university"]
            .extra["min_value"],
            1,
        )

        self.assertEqual(
            DepartmentFilter
            .base_filters["university"]
            .extra["min_value"],
            1,
        )

        self.assertEqual(
            DepartmentFilter
            .base_filters["faculty"]
            .extra["min_value"],
            1,
        )