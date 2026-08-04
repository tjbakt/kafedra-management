from django.urls import reverse
from rest_framework import status

from apps.access_control.models import (
    SystemRole,
)
from apps.audit.models import AuditEvent
from tests.assertions import (
    ApiResponseAssertionsMixin,
)
from tests.base import BaseAPITestCase
from tests.factories import (
    AuditEventFactory,
    DepartmentFactory,
    UserFactory,
    UserRoleAssignmentFactory,
)


class AuditApiBase(
    ApiResponseAssertionsMixin,
    BaseAPITestCase,
):
    def results(self, response):
        if isinstance(response.data, list):
            return response.data

        return response.data["results"]


class AuditEventApiTests(AuditApiBase):
    def setUp(self):
        self.user = self.create_global_admin()

        self.authenticate_with_jwt(
            user=self.user
        )

    def test_requires_authentication(self):
        self.logout_client()

        response = self.client.get(
            reverse("audit-event-list")
        )

        self.assert_authentication_required(
            response
        )

    def test_global_admin_can_view_events(
        self,
    ):
        expected = AuditEventFactory()

        response = self.client.get(
            reverse("audit-event-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertIn(expected.pk, ids)

    def test_post_is_not_allowed(self):
        response = self.client.post(
            reverse("audit-event-list"),
            {
                "action": AuditEvent.Action.CREATE,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_patch_is_not_allowed(self):
        event = AuditEventFactory()

        response = self.client.patch(
            reverse(
                "audit-event-detail",
                kwargs={"pk": event.pk},
            ),
            {
                "reason": "Изменение",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_delete_is_not_allowed(self):
        event = AuditEventFactory()

        response = self.client.delete(
            reverse(
                "audit-event-detail",
                kwargs={"pk": event.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_filter_by_action(self):
        expected = AuditEventFactory(
            action=AuditEvent.Action.APPROVE,
        )
        AuditEventFactory(
            action=AuditEvent.Action.CANCEL,
        )

        response = self.client.get(
            reverse("audit-event-list"),
            {
                "action": (
                    AuditEvent.Action.APPROVE
                ),
            },
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertEqual(ids, {expected.pk})

    def test_object_history_requires_params(
        self,
    ):
        response = self.client.get(
            reverse(
                "audit-event-object-history"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "app_label",
            response.data["detail"],
        )
        self.assertIn(
            "model",
            response.data["detail"],
        )
        self.assertIn(
            "object_id",
            response.data["detail"],
        )

    def test_object_history(self):
        expected = AuditEventFactory(
            object_id="101",
        )

        AuditEventFactory(
            content_type=expected.content_type,
            object_id="102",
        )

        response = self.client.get(
            reverse(
                "audit-event-object-history"
            ),
            {
                "app_label": (
                    expected.content_type.app_label
                ),
                "model": (
                    expected.content_type.model
                ),
                "object_id": "101",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertEqual(ids, {expected.pk})


class AuditScopeApiTests(AuditApiBase):
    def test_department_head_sees_department_events(
        self,
    ):
        department = DepartmentFactory()
        other_department = DepartmentFactory()

        head_user = UserFactory()

        UserRoleAssignmentFactory.department_role(
            user=head_user,
            department=department,
            role_code=(
                SystemRole.Code.DEPARTMENT_HEAD
            ),
        )

        expected = AuditEventFactory(
            department_id=department.pk,
        )
        hidden = AuditEventFactory(
            department_id=other_department.pk,
        )

        self.authenticate_with_jwt(
            user=head_user
        )

        response = self.client.get(
            reverse("audit-event-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertIn(expected.pk, ids)
        self.assertNotIn(hidden.pk, ids)

    def test_user_without_audit_permission_rejected(
        self,
    ):
        ordinary_user = UserFactory()

        self.authenticate_with_jwt(
            user=ordinary_user
        )

        response = self.client.get(
            reverse("audit-event-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )