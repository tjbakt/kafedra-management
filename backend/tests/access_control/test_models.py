from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.access_control.models import (
    SystemRole,
    UserRoleAssignment,
)
from tests.factories import (
    DepartmentFactory,
    FacultyFactory,
    StaffMemberFactory,
    SystemRoleFactory,
    UniversityFactory,
    UserFactory,
    UserRoleAssignmentFactory,
)


class SystemRoleModelTests(TestCase):
    def test_string_representation(self):
        role = SystemRoleFactory(
            name_ru="Тестовая роль",
        )

        self.assertEqual(
            str(role),
            "Тестовая роль",
        )

    def test_role_codes_are_complete(self):
        expected_codes = {
            "system_admin",
            "academic_office",
            "hr_officer",
            "dean_office",
            "department_head",
            "teacher",
            "viewer",
        }

        self.assertEqual(
            {
                value
                for value, _label
                in SystemRole.Code.choices
            },
            expected_codes,
        )


class UserRoleAssignmentModelTests(
    TestCase
):
    def test_string_representation(self):
        assignment = (
            UserRoleAssignmentFactory
            .global_role()
        )

        user_name = (
                assignment.user.get_full_name()
                or assignment.user.username
        )

        self.assertEqual(
            str(assignment),
            (
                f"{user_name} — "
                f"{assignment.role.name_ru}"
            ),
        )

    def test_current_assignment(self):
        assignment = (
            UserRoleAssignmentFactory
            .global_role()
        )

        self.assertTrue(
            assignment.is_current
        )

    def test_future_assignment_is_not_current(
        self,
    ):
        assignment = (
            UserRoleAssignmentFactory
            .global_role(
                valid_from=(
                    timezone.localdate()
                    + timedelta(days=1)
                ),
            )
        )

        self.assertFalse(
            assignment.is_current
        )

    def test_expired_assignment_is_not_current(
        self,
    ):
        assignment = (
            UserRoleAssignmentFactory
            .global_role(
                valid_from=(
                    timezone.localdate()
                    - timedelta(days=10)
                ),
                valid_until=(
                    timezone.localdate()
                    - timedelta(days=1)
                ),
            )
        )

        self.assertFalse(
            assignment.is_current
        )

    def test_inactive_assignment_is_not_current(
        self,
    ):
        assignment = (
            UserRoleAssignmentFactory
            .global_role(
                is_active=False,
            )
        )

        self.assertFalse(
            assignment.is_current
        )

    def test_archived_assignment_is_not_current(
        self,
    ):
        assignment = (
            UserRoleAssignmentFactory
            .global_role()
        )

        assignment.archive()

        self.assertFalse(
            assignment.is_current
        )

    def test_end_date_before_start_is_invalid(
        self,
    ):
        assignment = (
            UserRoleAssignmentFactory
            .build(
                valid_from=timezone.localdate(),
                valid_until=(
                    timezone.localdate()
                    - timedelta(days=1)
                ),
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            assignment.full_clean()

        self.assertIn(
            "valid_until",
            context.exception.message_dict,
        )

    def test_global_scope_rejects_department(
        self,
    ):
        assignment = (
            UserRoleAssignmentFactory
            .build(
                scope_type=(
                    UserRoleAssignment
                    .ScopeType
                    .GLOBAL
                ),
                department=DepartmentFactory(),
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            assignment.full_clean()

        self.assertIn(
            "scope_type",
            context.exception.message_dict,
        )

    def test_university_scope_requires_university(
        self,
    ):
        assignment = (
            UserRoleAssignmentFactory
            .build(
                scope_type=(
                    UserRoleAssignment
                    .ScopeType
                    .UNIVERSITY
                ),
                university=None,
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            assignment.full_clean()

        self.assertIn(
            "university",
            context.exception.message_dict,
        )

    def test_faculty_scope_requires_faculty(self):
        assignment = (
            UserRoleAssignmentFactory
            .build(
                scope_type=(
                    UserRoleAssignment
                    .ScopeType
                    .FACULTY
                ),
                faculty=None,
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            assignment.full_clean()

        self.assertIn(
            "faculty",
            context.exception.message_dict,
        )

    def test_department_scope_requires_department(
        self,
    ):
        assignment = (
            UserRoleAssignmentFactory
            .build(
                scope_type=(
                    UserRoleAssignment
                    .ScopeType
                    .DEPARTMENT
                ),
                department=None,
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            assignment.full_clean()

        self.assertIn(
            "department",
            context.exception.message_dict,
        )

    def test_self_scope_requires_staff_member(
        self,
    ):
        assignment = (
            UserRoleAssignmentFactory
            .build(
                scope_type=(
                    UserRoleAssignment
                    .ScopeType
                    .SELF
                ),
                staff_member=None,
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            assignment.full_clean()

        self.assertIn(
            "staff_member",
            context.exception.message_dict,
        )

    def test_teacher_role_requires_self_scope(
        self,
    ):
        role = SystemRoleFactory(
            code=SystemRole.Code.TEACHER,
        )

        assignment = (
            UserRoleAssignmentFactory
            .build(
                role=role,
                scope_type=(
                    UserRoleAssignment
                    .ScopeType
                    .GLOBAL
                ),
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            assignment.full_clean()

        self.assertIn(
            "scope_type",
            context.exception.message_dict,
        )

    def test_department_head_requires_department_scope(
        self,
    ):
        role = SystemRoleFactory(
            code=(
                SystemRole.Code.DEPARTMENT_HEAD
            ),
        )

        assignment = (
            UserRoleAssignmentFactory
            .build(
                role=role,
                scope_type=(
                    UserRoleAssignment
                    .ScopeType
                    .GLOBAL
                ),
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            assignment.full_clean()

        self.assertIn(
            "scope_type",
            context.exception.message_dict,
        )

    def test_department_must_belong_to_faculty(
        self,
    ):
        department = DepartmentFactory()
        other_faculty = FacultyFactory()

        assignment = (
            UserRoleAssignmentFactory
            .build(
                scope_type=(
                    UserRoleAssignment
                    .ScopeType
                    .DEPARTMENT
                ),
                department=department,
                faculty=other_faculty,
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            assignment.full_clean()

        self.assertIn(
            "department",
            context.exception.message_dict,
        )