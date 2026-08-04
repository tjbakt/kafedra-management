from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.notifications.models import (
    Notification,
    UserTask,
)
from tests.factories import (
    NotificationFactory,
    UserTaskFactory,
)


class NotificationModelTests(TestCase):
    def test_string_representation(self):
        notification = NotificationFactory(
            title="Новая задача",
        )

        self.assertEqual(
            str(notification),
            (
                f"{notification.recipient}: "
                "Новая задача"
            ),
        )

    def test_mark_as_read(self):
        notification = NotificationFactory(
            is_read=False,
            read_at=None,
        )

        notification.mark_as_read()
        notification.refresh_from_db()

        self.assertTrue(notification.is_read)
        self.assertIsNotNone(
            notification.read_at
        )

    def test_mark_as_read_is_idempotent(self):
        notification = NotificationFactory()
        notification.mark_as_read()

        first_read_at = notification.read_at

        notification.mark_as_read()
        notification.refresh_from_db()

        self.assertEqual(
            notification.read_at,
            first_read_at,
        )

    def test_archive(self):
        notification = NotificationFactory()

        notification.archive()
        notification.refresh_from_db()

        self.assertTrue(
            notification.is_archived
        )
        self.assertIsNotNone(
            notification.archived_at
        )


class UserTaskModelTests(TestCase):
    def test_string_representation(self):
        task = UserTaskFactory(
            title="Проверить план",
        )

        self.assertEqual(
            str(task),
            (
                f"{task.assignee}: "
                "Проверить план"
            ),
        )

    def test_open_past_task_is_overdue(self):
        task = UserTaskFactory(
            status=UserTask.Status.OPEN,
            due_date=(
                timezone.localdate()
                - timedelta(days=1)
            ),
        )

        self.assertTrue(task.is_overdue)

    def test_in_progress_past_task_is_overdue(
        self,
    ):
        task = UserTaskFactory(
            status=(
                UserTask.Status.IN_PROGRESS
            ),
            due_date=(
                timezone.localdate()
                - timedelta(days=1)
            ),
        )

        self.assertTrue(task.is_overdue)

    def test_completed_task_is_not_overdue(
        self,
    ):
        task = UserTaskFactory.completed(
            due_date=(
                timezone.localdate()
                - timedelta(days=1)
            ),
        )

        self.assertFalse(task.is_overdue)

    def test_task_without_due_date_not_overdue(
        self,
    ):
        task = UserTaskFactory(
            due_date=None,
        )

        self.assertFalse(task.is_overdue)