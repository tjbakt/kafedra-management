from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

from apps.access_control.models import (
    SystemRole,
    UserRoleAssignment,
)
from apps.organizations.models import (
    Department,
    Faculty,
    University,
)

from tests.assertions import (
    ApiResponseAssertionsMixin,
)
from tests.base import BaseAPITestCase
from tests.factories import (
    DepartmentFactory,
    SystemRoleFactory,
    UserFactory,
    UserRoleAssignmentFactory,
)


User = get_user_model()


class FactorySmokeTests(TestCase):
    def test_user_factory(self):
        user = UserFactory()

        self.assertIsInstance(
            user,
            User,
        )
        self.assertTrue(
            user.check_password(
                "test-password-123"
            )
        )
        self.assertTrue(user.is_active)

    def test_organization_factories(self):
        department = DepartmentFactory()

        self.assertIsInstance(
            department,
            Department,
        )
        self.assertIsInstance(
            department.faculty,
            Faculty,
        )
        self.assertIsInstance(
            department.faculty.university,
            University,
        )

        self.assertFalse(
            department.is_archived
        )
        self.assertTrue(
            department.is_active
        )

    def test_role_factory(self):
        role = SystemRoleFactory(
            code=(
                SystemRole.Code.SYSTEM_ADMIN
            )
        )

        self.assertEqual(
            role.code,
            SystemRole.Code.SYSTEM_ADMIN,
        )
        self.assertTrue(role.is_active)

    def test_global_role_assignment_factory(
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

        self.assertIsInstance(
            assignment,
            UserRoleAssignment,
        )
        self.assertEqual(
            assignment.user,
            user,
        )
        self.assertEqual(
            assignment.scope_type,
            (
                UserRoleAssignment
                .ScopeType
                .GLOBAL
            ),
        )
        self.assertIsNone(
            assignment.university
        )
        self.assertIsNone(
            assignment.faculty
        )
        self.assertIsNone(
            assignment.department
        )
        self.assertTrue(
            assignment.is_current
        )

    def test_department_role_assignment_factory(
        self,
    ):
        user = UserFactory()

        assignment = (
            UserRoleAssignmentFactory
            .department_role(
                user=user,
            )
        )

        self.assertEqual(
            assignment.scope_type,
            (
                UserRoleAssignment
                .ScopeType
                .DEPARTMENT
            ),
        )
        self.assertIsNotNone(
            assignment.department
        )
        self.assertEqual(
            assignment.role.code,
            (
                SystemRole
                .Code
                .DEPARTMENT_HEAD
            ),
        )


class ApiInfrastructureSmokeTests(
    ApiResponseAssertionsMixin,
    BaseAPITestCase,
):
    def test_force_authentication(self):
        user = self.authenticate()

        self.assertTrue(
            user.is_authenticated
        )

    def test_jwt_token_can_be_created(self):
        user = self.create_global_admin()

        self.authenticate_with_jwt(
            user=user
        )

        self.assertTrue(
            user.is_active
        )

    def test_health_check_available(self):
        response = self.client.get(
            "/api/v1/health/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )