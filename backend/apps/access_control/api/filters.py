from django_filters import rest_framework as filters

from apps.access_control.models import (
    SystemRole,
    UserRoleAssignment,
)


class SystemRoleFilter(filters.FilterSet):
    is_active = filters.BooleanFilter()

    class Meta:
        model = SystemRole
        fields = (
            "code",
            "is_active",
        )


class UserRoleAssignmentFilter(filters.FilterSet):
    user = filters.NumberFilter(
        field_name="user_id",
    )
    role = filters.NumberFilter(
        field_name="role_id",
    )
    role_code = filters.CharFilter(
        field_name="role__code",
    )
    scope_type = filters.ChoiceFilter(
        choices=UserRoleAssignment.ScopeType.choices,
    )
    university = filters.NumberFilter(
        field_name="university_id",
    )
    faculty = filters.NumberFilter(
        field_name="faculty_id",
    )
    department = filters.NumberFilter(
        field_name="department_id",
    )
    staff_member = filters.NumberFilter(
        field_name="staff_member_id",
    )
    is_active = filters.BooleanFilter()

    class Meta:
        model = UserRoleAssignment
        fields = (
            "user",
            "role",
            "role_code",
            "scope_type",
            "university",
            "faculty",
            "department",
            "staff_member",
            "is_active",
        )