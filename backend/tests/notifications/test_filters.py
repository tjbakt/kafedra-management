from django.test import SimpleTestCase

from apps.notifications.api.filters import (
    NotificationFilter,
    UserTaskFilter,
)


class NotificationFilterDeclarationTests(
    SimpleTestCase
):
    def test_notification_filters(self):
        self.assertEqual(
            set(
                NotificationFilter.base_filters
            ),
            {
                "notification_type",
                "is_read",
                "is_archived",
                "created_from",
                "created_until",
            },
        )

    def test_task_filters(self):
        self.assertEqual(
            set(UserTaskFilter.base_filters),
            {
                "task_type",
                "status",
                "priority",
                "due_from",
                "due_until",
                "overdue",
            },
        )