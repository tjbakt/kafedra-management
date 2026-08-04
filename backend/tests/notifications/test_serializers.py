from django.test import TestCase

from apps.notifications.api.serializers import (
    NotificationSerializer,
    UserTaskSerializer,
)
from tests.factories import (
    NotificationFactory,
    UserTaskFactory,
)


class NotificationSerializerTests(
    TestCase
):
    def test_output_fields(self):
        notification = NotificationFactory()

        serializer = NotificationSerializer(
            notification
        )

        self.assertEqual(
            serializer.data["recipient"],
            notification.recipient_id,
        )
        self.assertEqual(
            serializer.data[
                "notification_type"
            ],
            notification.notification_type,
        )
        self.assertIn(
            "notification_type_name",
            serializer.data,
        )

    def test_all_fields_are_read_only(self):
        notification = NotificationFactory()

        serializer = NotificationSerializer(
            notification,
            data={
                "title": "Изменённый заголовок",
                "is_read": True,
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        updated = serializer.save()

        self.assertNotEqual(
            updated.title,
            "Изменённый заголовок",
        )
        self.assertFalse(updated.is_read)


class UserTaskSerializerTests(TestCase):
    def test_related_names_and_status(self):
        task = UserTaskFactory()

        serializer = UserTaskSerializer(task)

        self.assertEqual(
            serializer.data["assignee"],
            task.assignee_id,
        )
        self.assertEqual(
            serializer.data["status"],
            task.status,
        )
        self.assertIn(
            "assignee_name",
            serializer.data,
        )
        self.assertIn(
            "created_by_name",
            serializer.data,
        )
        self.assertIn(
            "is_overdue",
            serializer.data,
        )

    def test_all_fields_are_read_only(self):
        task = UserTaskFactory()

        serializer = UserTaskSerializer(
            task,
            data={
                "title": "Изменённая задача",
                "status": "completed",
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        updated = serializer.save()

        self.assertNotEqual(
            updated.title,
            "Изменённая задача",
        )
        self.assertNotEqual(
            updated.status,
            "completed",
        )