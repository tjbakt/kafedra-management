from django.urls import reverse
from rest_framework import status

from apps.access_control.models import (
    SystemRole,
    UserRoleAssignment,
)
from apps.audit.models import AuditEvent
from tests.assertions import (
    ApiResponseAssertionsMixin,
)
from tests.base import BaseAPITestCase
from tests.factories import (
    DepartmentFactory,
    StaffMemberFactory,
    SystemRoleFactory,
    UserFactory,
    UserRoleAssignmentFactory,
)
from datetime import timedelta

from django.utils import timezone


class AccessControlApiBase(
    ApiResponseAssertionsMixin,
    BaseAPITestCase,
):
    def setUp(self):
        self.admin = self.create_global_admin()

        self.authenticate_with_jwt(
            user=self.admin
        )

    def results(self, response):
        if isinstance(response.data, list):
            return response.data

        return response.data["results"]


class SystemRoleApiTests(
    AccessControlApiBase
):
    def setUp(self):
        super().setUp()

        self.list_url = reverse(
            "system-role-list"
        )

    def detail_url(self, role):
        return reverse(
            "system-role-detail",
            kwargs={"pk": role.pk},
        )

    def test_anonymous_user_is_rejected(self):
        self.logout_client()

        response = self.client.get(
            self.list_url
        )

        self.assert_authentication_required(
            response
        )

    def test_non_admin_is_forbidden(self):
        user = UserFactory()

        self.authenticate_with_jwt(
            user=user
        )

        response = self.client.get(
            self.list_url
        )

        self.assert_permission_denied(
            response
        )

    def test_admin_can_list_roles(self):
        SystemRoleFactory(
            code=SystemRole.Code.VIEWER,
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_admin_can_create_role(self):
        response = self.client.post(
            self.list_url,
            {
                "code": (
                    SystemRole.Code.HR_OFFICER
                ),
                "name_ru": "Кадровая служба",
                "name_uz": "Kadrlar bo‘limi",
                "description": "",
                "is_active": True,
                "sort_order": 10,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        role = SystemRole.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            role.created_by,
            self.admin,
        )
        self.assertEqual(
            role.updated_by,
            self.admin,
        )

    def test_filter_by_code(self):
        expected = SystemRoleFactory(
            code=SystemRole.Code.HR_OFFICER,
        )
        SystemRoleFactory(
            code=SystemRole.Code.VIEWER,
        )

        response = self.client.get(
            self.list_url,
            {
                "code": (
                    SystemRole.Code.HR_OFFICER
                )
            },
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertEqual(
            ids,
            {expected.pk},
        )

    def test_archive_and_restore_role(self):
        role = SystemRoleFactory(
            code=SystemRole.Code.VIEWER,
        )

        delete_response = self.client.delete(
            self.detail_url(role)
        )

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_200_OK,
        )

        restore_response = self.client.post(
            reverse(
                "system-role-restore",
                kwargs={"pk": role.pk},
            ),
            {},
            format="json",
        )

        self.assertEqual(
            restore_response.status_code,
            status.HTTP_200_OK,
        )

        role.refresh_from_db()

        self.assertFalse(
            role.is_archived
        )



class UserRoleAssignmentApiTests(
    AccessControlApiBase
):
    def setUp(self):
        super().setUp()

        self.list_url = reverse(
            "user-role-assignment-list"
        )

    def detail_url(self, assignment):
        return reverse(
            "user-role-assignment-detail",
            kwargs={
                "pk": assignment.pk,
            },
        )

    def test_non_admin_cannot_list_assignments(
        self,
    ):
        user = UserFactory()

        self.authenticate_with_jwt(
            user=user
        )

        response = self.client.get(
            self.list_url
        )

        self.assert_permission_denied(
            response
        )

    def test_admin_can_create_global_assignment(
        self,
    ):
        user = UserFactory()
        role = SystemRoleFactory(
            code=SystemRole.Code.VIEWER,
        )

        response = self.client.post(
            self.list_url,
            {
                "user": user.pk,
                "role": role.pk,
                "scope_type": (
                    UserRoleAssignment
                    .ScopeType
                    .GLOBAL
                ),
                "valid_from": (
                    timezone.localdate()
                    .isoformat()
                ),
                "is_active": True,
                "notes": "",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        assignment = (
            UserRoleAssignment.objects.get(
                pk=response.data["id"]
            )
        )

        self.assertEqual(
            assignment.created_by,
            self.admin,
        )
        self.assertEqual(
            assignment.updated_by,
            self.admin,
        )

        self.assertTrue(
            AuditEvent.objects.filter(
                actor=self.admin,
                action=(
                    AuditEvent.Action.CREATE
                ),
            ).exists()
        )

    def test_global_assignment_rejects_department(
        self,
    ):
        user = UserFactory()
        role = SystemRoleFactory(
            code=SystemRole.Code.VIEWER,
        )
        department = DepartmentFactory()

        response = self.client.post(
            self.list_url,
            {
                "user": user.pk,
                "role": role.pk,
                "scope_type": (
                    UserRoleAssignment
                    .ScopeType
                    .GLOBAL
                ),
                "department": department.pk,
                "valid_from": (
                    timezone.localdate()
                    .isoformat()
                ),
                "is_active": True,
            },
            format="json",
        )

        self.assert_validation_error(
            response,
            field="scope_type",
        )

    def test_create_teacher_assignment(self):
        user = UserFactory()
        staff_member = StaffMemberFactory(
            user=user,
        )
        role = SystemRoleFactory(
            code=SystemRole.Code.TEACHER,
        )

        response = self.client.post(
            self.list_url,
            {
                "user": user.pk,
                "role": role.pk,
                "scope_type": (
                    UserRoleAssignment
                    .ScopeType
                    .SELF
                ),
                "staff_member": (
                    staff_member.pk
                ),
                "valid_from": (
                    timezone.localdate()
                    .isoformat()
                ),
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_teacher_rejects_global_scope(self):
        user = UserFactory()
        role = SystemRoleFactory(
            code=SystemRole.Code.TEACHER,
        )

        response = self.client.post(
            self.list_url,
            {
                "user": user.pk,
                "role": role.pk,
                "scope_type": (
                    UserRoleAssignment
                    .ScopeType
                    .GLOBAL
                ),
                "valid_from": (
                    timezone.localdate()
                    .isoformat()
                ),
                "is_active": True,
            },
            format="json",
        )

        self.assert_validation_error(
            response,
            field="scope_type",
        )

    def test_update_creates_audit_event(self):
        assignment = (
            UserRoleAssignmentFactory
            .global_role(
                role_code=(
                    SystemRole.Code.VIEWER
                ),
            )
        )

        response = self.client.patch(
            self.detail_url(assignment),
            {
                "notes": "Изменено тестом",
                "is_active": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        assignment.refresh_from_db()

        self.assertEqual(
            assignment.updated_by,
            self.admin,
        )
        self.assertFalse(
            assignment.is_active,
        )

        self.assertTrue(
            AuditEvent.objects.filter(
                actor=self.admin,
                action=(
                    AuditEvent.Action.UPDATE
                ),
            ).exists()
        )

    def test_filter_by_role_code(self):
        expected = (
            UserRoleAssignmentFactory
            .global_role(
                role_code=(
                    SystemRole.Code.HR_OFFICER
                ),
            )
        )

        (
            UserRoleAssignmentFactory
            .global_role(
                role_code=(
                    SystemRole.Code.VIEWER
                ),
            )
        )

        response = self.client.get(
            self.list_url,
            {
                "role_code": (
                    SystemRole.Code.HR_OFFICER
                )
            },
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertIn(
            expected.pk,
            ids,
        )

    def test_archive_and_restore_assignment(
        self,
    ):
        assignment = (
            UserRoleAssignmentFactory
            .global_role(
                role_code=(
                    SystemRole.Code.VIEWER
                ),
            )
        )

        delete_response = self.client.delete(
            self.detail_url(assignment)
        )

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_200_OK,
        )

        restore_response = self.client.post(
            reverse(
                "user-role-assignment-restore",
                kwargs={
                    "pk": assignment.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            restore_response.status_code,
            status.HTTP_200_OK,
        )

        assignment.refresh_from_db()

        self.assertFalse(
            assignment.is_archived,
        )

    def test_my_access_requires_authentication(
        self,
    ):
        self.logout_client()

        response = self.client.get(
            reverse(
                "user-role-assignment-my-access"
            )
        )

        self.assert_authentication_required(
            response
        )

    def test_my_access_available_to_non_admin(
        self,
    ):
        user = UserFactory()

        assignment = (
            UserRoleAssignmentFactory
            .global_role(
                user=user,
                role_code=(
                    SystemRole.Code.VIEWER
                ),
            )
        )

        self.authenticate_with_jwt(
            user=user
        )

        response = self.client.get(
            reverse(
                "user-role-assignment-my-access"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["user"],
            user.pk,
        )
        self.assertEqual(
            response.data["username"],
            user.username,
        )

        role_ids = {
            item["id"]
            for item in response.data["roles"]
        }

        self.assertIn(
            assignment.pk,
            role_ids,
        )

    def test_my_access_excludes_expired_role(
        self,
    ):
        user = UserFactory()

        UserRoleAssignmentFactory.global_role(
            user=user,
            role_code=(
                SystemRole.Code.VIEWER
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

        self.authenticate_with_jwt(
            user=user
        )

        response = self.client.get(
            reverse(
                "user-role-assignment-my-access"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["roles"],
            [],
        )