from django.db.models import Q
from django.utils import timezone

from django.contrib.auth import get_user_model

from apps.access_control.models import (
    SystemRole,
    UserRoleAssignment,
)


class AccessService:
    """
    Централизованная проверка активных ролей пользователя.
    """

    @classmethod
    def active_assignments(cls, user):
        if not user or not user.is_authenticated:
            return UserRoleAssignment.objects.none()

        return cls.active_assignments_queryset().filter(
            user=user,
        )

    @classmethod
    def has_role(cls, user, *role_codes):
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return cls.active_assignments(user).filter(
            role__code__in=role_codes,
        ).exists()

    @classmethod
    def has_global_role(cls, user, *role_codes):
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return cls.active_assignments(user).filter(
            role__code__in=role_codes,
            scope_type=UserRoleAssignment.ScopeType.GLOBAL,
        ).exists()

    @classmethod
    def accessible_university_ids(cls, user):
        assignments = cls.active_assignments(user)

        if user.is_superuser or assignments.filter(
            scope_type=UserRoleAssignment.ScopeType.GLOBAL,
        ).exists():
            return None

        ids = set()

        for assignment in assignments:
            if assignment.university_id:
                ids.add(assignment.university_id)

            if assignment.faculty_id:
                ids.add(assignment.faculty.university_id)

            if assignment.department_id:
                ids.add(
                    assignment.department.faculty.university_id
                )

        return ids

    @classmethod
    def accessible_faculty_ids(cls, user):
        assignments = cls.active_assignments(user)

        if user.is_superuser or assignments.filter(
            scope_type=UserRoleAssignment.ScopeType.GLOBAL,
        ).exists():
            return None

        ids = set()

        for assignment in assignments:
            if assignment.faculty_id:
                ids.add(assignment.faculty_id)

            if assignment.department_id:
                ids.add(assignment.department.faculty_id)

        return ids

    @classmethod
    def accessible_department_ids(
        cls,
        user,
        *,
        role_codes=None,
    ):
        assignments = cls.active_assignments(user)

        if role_codes:
            assignments = assignments.filter(
                role__code__in=role_codes,
            )

        if user.is_superuser or assignments.filter(
            scope_type=UserRoleAssignment.ScopeType.GLOBAL,
        ).exists():
            return None

        ids = set()

        for assignment in assignments:
            if assignment.department_id:
                ids.add(assignment.department_id)

        return ids

    @classmethod
    def accessible_staff_member_ids(cls, user):
        assignments = cls.active_assignments(user)

        if user.is_superuser or assignments.filter(
            scope_type=UserRoleAssignment.ScopeType.GLOBAL,
        ).exists():
            return None

        ids = set()

        for assignment in assignments:
            if assignment.staff_member_id:
                ids.add(assignment.staff_member_id)

        return ids

    @classmethod
    def can_manage_department(cls, user, department_id):
        if cls.has_global_role(
            user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.ACADEMIC_OFFICE,
        ):
            return True

        return cls.active_assignments(user).filter(
            role__code=SystemRole.Code.DEPARTMENT_HEAD,
            scope_type=UserRoleAssignment.ScopeType.DEPARTMENT,
            department_id=department_id,
        ).exists()

    @classmethod
    def can_manage_staff_member(cls, user, staff_member):
        if cls.has_global_role(
            user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.HR_OFFICER,
        ):
            return True

        department_ids = cls.accessible_department_ids(
            user,
            role_codes=(
                SystemRole.Code.DEPARTMENT_HEAD,
            ),
        )

        if department_ids is None:
            return True

        return staff_member.employments.filter(
            department_id__in=department_ids,
            is_active=True,
            is_archived=False,
        ).exists()

    @classmethod
    def is_own_staff_member(cls, user, staff_member_id):
        return cls.active_assignments(user).filter(
            role__code=SystemRole.Code.TEACHER,
            scope_type=UserRoleAssignment.ScopeType.SELF,
            staff_member_id=staff_member_id,
        ).exists()

    @classmethod
    def users_with_role(
            cls,
            *,
            role_code,
            university_id=None,
            faculty_id=None,
            department_id=None,
    ):
        User = get_user_model()

        assignments = cls.active_assignments_queryset().filter(
            role__code=role_code,
        )

        if department_id is not None:
            assignments = assignments.filter(
                Q(
                    scope_type=UserRoleAssignment.ScopeType.GLOBAL
                )
                | Q(
                    scope_type=(
                        UserRoleAssignment.ScopeType.DEPARTMENT
                    ),
                    department_id=department_id,
                )
            )
        elif faculty_id is not None:
            assignments = assignments.filter(
                Q(
                    scope_type=UserRoleAssignment.ScopeType.GLOBAL
                )
                | Q(
                    scope_type=UserRoleAssignment.ScopeType.FACULTY,
                    faculty_id=faculty_id,
                )
            )
        elif university_id is not None:
            assignments = assignments.filter(
                Q(
                    scope_type=UserRoleAssignment.ScopeType.GLOBAL
                )
                | Q(
                    scope_type=(
                        UserRoleAssignment.ScopeType.UNIVERSITY
                    ),
                    university_id=university_id,
                )
            )

        return User.objects.filter(
            role_assignments__in=assignments
        ).distinct()

    @staticmethod
    def active_assignments_queryset():
        today = timezone.localdate()

        return (
            UserRoleAssignment.objects
            .select_related(
                "user",
                "role",
                "university",
                "faculty",
                "department",
                "staff_member",
            )
            .filter(
                is_active=True,
                is_archived=False,
                role__is_active=True,
                role__is_archived=False,
                valid_from__lte=today,
            )
            .filter(
                Q(valid_until__isnull=True)
                | Q(valid_until__gte=today)
            )
        )