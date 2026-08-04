from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.notifications.models import (
    Notification,
    UserTask,
)
from tests.assertions import (
    ApiResponseAssertionsMixin,
)
from tests.base import BaseAPITestCase
from tests.factories import (
    NotificationFactory,
    UserFactory,
    UserTaskFactory,
)


class NotificationApiBase(
    ApiResponseAssertionsMixin,
    BaseAPITestCase,
):
    def setUp(self):
        self.user = UserFactory()
        self.authenticate_with_jwt(
            user=self.user
        )

    def results(self, response):
        if isinstance(response.data, list):
            return response.data

        return response.data["results"]


class NotificationApiTests(
    NotificationApiBase
):
    def test_requires_authentication(self):
        self.logout_client()

        response = self.client.get(
            reverse("notification-list")
        )

        self.assert_authentication_required(
            response
        )

    def test_user_sees_only_own_notifications(
        self,
    ):
        expected = NotificationFactory(
            recipient=self.user,
        )
        NotificationFactory(
            recipient=UserFactory(),
        )

        response = self.client.get(
            reverse("notification-list")
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertEqual(ids, {expected.pk})

    def test_mark_read(self):
        notification = NotificationFactory(
            recipient=self.user,
        )

        response = self.client.post(
            reverse(
                "notification-mark-read",
                kwargs={
                    "pk": notification.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(
            response.data["is_read"]
        )

        notification.refresh_from_db()

        self.assertIsNotNone(
            notification.read_at
        )

    def test_cannot_mark_other_notification(
        self,
    ):
        notification = NotificationFactory(
            recipient=UserFactory(),
        )

        response = self.client.post(
            reverse(
                "notification-mark-read",
                kwargs={
                    "pk": notification.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_mark_all_read(self):
        NotificationFactory.create_batch(
            2,
            recipient=self.user,
        )
        NotificationFactory.read(
            recipient=self.user,
        )
        NotificationFactory(
            recipient=UserFactory(),
        )

        response = self.client.post(
            reverse(
                "notification-mark-all-read"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["updated_count"],
            2,
        )

        self.assertFalse(
            Notification.objects.filter(
                recipient=self.user,
                is_read=False,
                is_archived=False,
            ).exists()
        )

    def test_archive(self):
        notification = NotificationFactory(
            recipient=self.user,
        )

        response = self.client.post(
            reverse(
                "notification-archive",
                kwargs={
                    "pk": notification.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(
            response.data["is_archived"]
        )

    def test_unread_count(self):
        NotificationFactory.create_batch(
            2,
            recipient=self.user,
        )
        NotificationFactory.read(
            recipient=self.user,
        )
        NotificationFactory.archived(
            recipient=self.user,
        )

        response = self.client.get(
            reverse(
                "notification-unread-count"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["unread_count"],
            2,
        )

    def test_filter_by_type(self):
        expected = NotificationFactory(
            recipient=self.user,
            notification_type=(
                Notification.Type.WARNING
            ),
        )
        NotificationFactory(
            recipient=self.user,
            notification_type=(
                Notification.Type.INFO
            ),
        )

        response = self.client.get(
            reverse("notification-list"),
            {
                "notification_type": (
                    Notification.Type.WARNING
                ),
            },
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertEqual(ids, {expected.pk})


class UserTaskApiTests(NotificationApiBase):
    def test_user_sees_only_own_tasks(self):
        expected = UserTaskFactory(
            assignee=self.user,
        )
        UserTaskFactory(
            assignee=UserFactory(),
        )

        response = self.client.get(
            reverse("user-task-list")
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertEqual(ids, {expected.pk})

    def test_start_task(self):
        task = UserTaskFactory(
            assignee=self.user,
            status=UserTask.Status.OPEN,
        )

        response = self.client.post(
            reverse(
                "user-task-start",
                kwargs={"pk": task.pk},
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["status"],
            UserTask.Status.IN_PROGRESS,
        )

    def test_start_non_open_task_rejected(
        self,
    ):
        task = UserTaskFactory.completed(
            assignee=self.user,
        )

        response = self.client.post(
            reverse(
                "user-task-start",
                kwargs={"pk": task.pk},
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_complete_task(self):
        task = UserTaskFactory.in_progress(
            assignee=self.user,
        )

        response = self.client.post(
            reverse(
                "user-task-complete",
                kwargs={"pk": task.pk},
            ),
            {
                "completion_comment": (
                    "Работа завершена."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["status"],
            UserTask.Status.COMPLETED,
        )
        self.assertEqual(
            response.data[
                "completion_comment"
            ],
            "Работа завершена.",
        )

    def test_complete_cancelled_task_rejected(
        self,
    ):
        task = UserTaskFactory(
            assignee=self.user,
            status=UserTask.Status.CANCELLED,
        )

        response = self.client.post(
            reverse(
                "user-task-complete",
                kwargs={"pk": task.pk},
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_summary(self):
        UserTaskFactory(
            assignee=self.user,
            status=UserTask.Status.OPEN,
        )
        UserTaskFactory.in_progress(
            assignee=self.user,
        )
        UserTaskFactory.completed(
            assignee=self.user,
        )
        UserTaskFactory.overdue(
            assignee=self.user,
        )
        UserTaskFactory(
            assignee=self.user,
            due_date=timezone.localdate(),
            status=UserTask.Status.OPEN,
        )

        response = self.client.get(
            reverse("user-task-summary")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["open"],
            3,
        )
        self.assertEqual(
            response.data["in_progress"],
            1,
        )
        self.assertEqual(
            response.data["completed"],
            1,
        )
        self.assertEqual(
            response.data["overdue"],
            1,
        )
        self.assertEqual(
            response.data["due_today"],
            1,
        )

    def test_inbox_excludes_completed(
        self,
    ):
        open_task = UserTaskFactory(
            assignee=self.user,
            status=UserTask.Status.OPEN,
        )
        progress_task = (
            UserTaskFactory.in_progress(
                assignee=self.user,
            )
        )
        completed_task = (
            UserTaskFactory.completed(
                assignee=self.user,
            )
        )

        response = self.client.get(
            reverse("user-task-inbox")
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertIn(open_task.pk, ids)
        self.assertIn(progress_task.pk, ids)
        self.assertNotIn(
            completed_task.pk,
            ids,
        )

    def test_filter_overdue(self):
        expected = UserTaskFactory(
            assignee=self.user,
            status=UserTask.Status.OPEN,
            due_date=(
                timezone.localdate()
                - timedelta(days=1)
            ),
        )
        UserTaskFactory(
            assignee=self.user,
            due_date=(
                timezone.localdate()
                + timedelta(days=1)
            ),
        )

        response = self.client.get(
            reverse("user-task-list"),
            {
                "overdue": "true",
            },
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertEqual(ids, {expected.pk})