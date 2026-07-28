from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.workload.services.workload_access_scope import (
    WorkloadAccessScope,
)


User = get_user_model()


class WorkloadAccessScopeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="scope-user",
            password="test-password-123",
        )

    def test_superuser_has_global_access(self):
        self.user.is_superuser = True
        self.user.save(
            update_fields=["is_superuser"]
        )

        scope = WorkloadAccessScope.for_user(
            self.user
        )

        self.assertTrue(scope.has_global_access)
        self.assertIsNone(scope.department_ids)
        self.assertIsNone(scope.staff_member_ids)

    @patch(
        "apps.workload.services.workload_access_scope."
        "AccessService.accessible_staff_member_ids"
    )
    @patch(
        "apps.workload.services.workload_access_scope."
        "AccessService.accessible_department_ids"
    )
    @patch(
        "apps.workload.services.workload_access_scope."
        "AccessService.has_global_role"
    )
    def test_local_scope_contains_allowed_ids(
        self,
        has_global_role_mock,
        accessible_department_ids_mock,
        accessible_staff_member_ids_mock,
    ):
        has_global_role_mock.return_value = False
        accessible_department_ids_mock.return_value = {
            10,
            20,
        }
        accessible_staff_member_ids_mock.return_value = {
            30,
        }

        scope = WorkloadAccessScope.for_user(
            self.user
        )

        self.assertEqual(
            scope.department_ids,
            {10, 20},
        )
        self.assertEqual(
            scope.staff_member_ids,
            {30},
        )

        self.assertTrue(
            scope.can_access_department(10)
        )
        self.assertTrue(
            scope.can_access_department("20")
        )
        self.assertFalse(
            scope.can_access_department(999)
        )

        self.assertTrue(
            scope.can_access_staff_member(30)
        )
        self.assertFalse(
            scope.can_access_staff_member(999)
        )

    @patch(
        "apps.workload.services.workload_access_scope."
        "AccessService.accessible_staff_member_ids"
    )
    @patch(
        "apps.workload.services.workload_access_scope."
        "AccessService.accessible_department_ids"
    )
    @patch(
        "apps.workload.services.workload_access_scope."
        "AccessService.has_global_role"
    )
    def test_user_without_assignments_has_empty_scope(
        self,
        has_global_role_mock,
        accessible_department_ids_mock,
        accessible_staff_member_ids_mock,
    ):
        has_global_role_mock.return_value = False
        accessible_department_ids_mock.return_value = set()
        accessible_staff_member_ids_mock.return_value = set()

        scope = WorkloadAccessScope.for_user(
            self.user
        )

        self.assertEqual(
            scope.department_ids,
            set(),
        )
        self.assertEqual(
            scope.staff_member_ids,
            set(),
        )
        self.assertFalse(
            scope.can_access_department(1)
        )
        self.assertFalse(
            scope.can_access_staff_member(1)
        )