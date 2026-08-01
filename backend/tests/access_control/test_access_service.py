from datetime import timedelta

from django.contrib.auth.models import (
    AnonymousUser,
)
from django.test import TestCase
from django.utils import timezone

from apps.access_control.models import (
    SystemRole,
)
from apps.access_control.services.access_service import (
    AccessService,
)
from tests.factories import (
    DepartmentFactory,
    FacultyFactory,
    StaffMemberFactory,
    SuperUserFactory,
    UniversityFactory,
    UserFactory,
    UserRoleAssignmentFactory,
)


class AccessServiceTests(TestCase):
    def test_anonymous_user_has_no_roles(self):
        user = AnonymousUser()

        self.assertFalse(
            AccessService.has_role(
                user,
                SystemRole.Code.SYSTEM_ADMIN,
            )
        )

    def test_superuser_has_every_role(self):
        user = SuperUserFactory()

        self.assertTrue(
            AccessService.has_role(
                user,
                SystemRole.Code.TEACHER,
            )
        )

        self.assertTrue(
            AccessService.has_global_role(
                user,
                SystemRole.Code.SYSTEM_ADMIN,
            )
        )

    def test_active_role_is_detected(self):
        user = UserFactory()

        UserRoleAssignmentFactory.global_role(
            user=user,
            role_code=(
                SystemRole.Code.SYSTEM_ADMIN
            ),
        )

        self.assertTrue(
            AccessService.has_role(
                user,
                SystemRole.Code.SYSTEM_ADMIN,
            )
        )

    def test_expired_role_is_ignored(self):
        user = UserFactory()

        UserRoleAssignmentFactory.global_role(
            user=user,
            role_code=(
                SystemRole.Code.SYSTEM_ADMIN
            ),
            valid_from=(
                timezone.localdate()
                - timedelta(days=10)
            ),
            valid_until=(
                timezone.localdate()
                - timedelta(days=1)
            ),
        )

        self.assertFalse(
            AccessService.has_role(
                user,
                SystemRole.Code.SYSTEM_ADMIN,
            )
        )

    def test_inactive_role_is_ignored(self):
        user = UserFactory()

        UserRoleAssignmentFactory.global_role(
            user=user,
            role_code=(
                SystemRole.Code.SYSTEM_ADMIN
            ),
            is_active=False,
        )

        self.assertFalse(
            AccessService.has_role(
                user,
                SystemRole.Code.SYSTEM_ADMIN,
            )
        )

    def test_archived_role_assignment_is_ignored(
        self,
    ):
        user = UserFactory()

        assignment = (
            UserRoleAssignmentFactory
            .global_role(
                user=user,
                role_code=(
                    SystemRole.Code.SYSTEM_ADMIN
                ),
            )
        )
        assignment.archive()

        self.assertFalse(
            AccessService.has_role(
                user,
                SystemRole.Code.SYSTEM_ADMIN,
            )
        )

    def test_global_scope_returns_all_access(
        self,
    ):
        user = UserFactory()

        UserRoleAssignmentFactory.global_role(
            user=user,
            role_code=(
                SystemRole.Code.SYSTEM_ADMIN
            ),
        )

        self.assertIsNone(
            AccessService
            .accessible_university_ids(user)
        )
        self.assertIsNone(
            AccessService
            .accessible_faculty_ids(user)
        )
        self.assertIsNone(
            AccessService
            .accessible_department_ids(user)
        )

    def test_department_scope_resolves_hierarchy(
        self,
    ):
        user = UserFactory()
        department = DepartmentFactory()

        UserRoleAssignmentFactory.department_role(
            user=user,
            department=department,
        )

        self.assertEqual(
            AccessService
            .accessible_university_ids(user),
            {
                department
                .faculty
                .university_id
            },
        )
        self.assertEqual(
            AccessService
            .accessible_faculty_ids(user),
            {
                department.faculty_id
            },
        )
        self.assertEqual(
            AccessService
            .accessible_department_ids(user),
            {
                department.pk
            },
        )

    def test_self_scope_resolves_staff_member(
        self,
    ):
        user = UserFactory()
        staff_member = StaffMemberFactory(
            user=user,
        )

        UserRoleAssignmentFactory.self_role(
            user=user,
            staff_member=staff_member,
        )

        self.assertEqual(
            AccessService
            .accessible_staff_member_ids(user),
            {
                staff_member.pk
            },
        )

        self.assertTrue(
            AccessService.is_own_staff_member(
                user,
                staff_member.pk,
            )
        )

    def test_department_head_can_manage_own_department(
        self,
    ):
        user = UserFactory()
        department = DepartmentFactory()

        UserRoleAssignmentFactory.department_role(
            user=user,
            department=department,
        )

        self.assertTrue(
            AccessService.can_manage_department(
                user,
                department.pk,
            )
        )

        self.assertFalse(
            AccessService.can_manage_department(
                user,
                DepartmentFactory().pk,
            )
        )

    def test_users_with_role_respects_department(
        self,
    ):
        department = DepartmentFactory()

        expected_user = UserFactory()
        other_user = UserFactory()

        UserRoleAssignmentFactory.department_role(
            user=expected_user,
            department=department,
        )

        UserRoleAssignmentFactory.department_role(
            user=other_user,
            department=DepartmentFactory(),
        )

        users = AccessService.users_with_role(
            role_code=(
                SystemRole.Code.DEPARTMENT_HEAD
            ),
            department_id=department.pk,
        )

        self.assertEqual(
            set(users),
            {
                expected_user,
            },
        )