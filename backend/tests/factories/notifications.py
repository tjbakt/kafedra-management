from datetime import timedelta

import factory
from django.utils import timezone

from apps.notifications.models import (
    Notification,
    UserTask,
)
from tests.factories.accounts import UserFactory


class NotificationFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = Notification

    recipient = factory.SubFactory(
        UserFactory
    )

    notification_type = Notification.Type.INFO

    title = factory.Sequence(
        lambda number: (
            f"Тестовое уведомление {number}"
        )
    )
    message = factory.Sequence(
        lambda number: (
            f"Текст тестового уведомления {number}"
        )
    )

    content_type = None
    object_id = None
    object_repr = ""
    action_url = ""
    metadata = factory.LazyFunction(dict)

    is_read = False
    read_at = None

    is_archived = False
    archived_at = None

    @classmethod
    def read(
        cls,
        **kwargs,
    ):
        return cls(
            is_read=True,
            read_at=timezone.now(),
            **kwargs,
        )

    @classmethod
    def archived(
        cls,
        **kwargs,
    ):
        return cls(
            is_archived=True,
            archived_at=timezone.now(),
            **kwargs,
        )


class UserTaskFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = UserTask

    assignee = factory.SubFactory(
        UserFactory
    )
    created_by = factory.SubFactory(
        UserFactory
    )

    task_type = UserTask.Type.OTHER
    status = UserTask.Status.OPEN
    priority = UserTask.Priority.NORMAL

    title = factory.Sequence(
        lambda number: (
            f"Тестовая задача {number}"
        )
    )
    description = ""

    content_type = None
    object_id = None
    object_repr = ""
    action_url = ""

    due_date = factory.LazyFunction(
        lambda: (
            timezone.localdate()
            + timedelta(days=7)
        )
    )

    started_at = None
    completed_at = None
    cancelled_at = None

    completion_comment = ""
    cancellation_reason = ""
    deduplication_key = ""
    metadata = factory.LazyFunction(dict)

    @classmethod
    def in_progress(
        cls,
        **kwargs,
    ):
        return cls(
            status=UserTask.Status.IN_PROGRESS,
            started_at=timezone.now(),
            **kwargs,
        )

    @classmethod
    def completed(
        cls,
        **kwargs,
    ):
        return cls(
            status=UserTask.Status.COMPLETED,
            completed_at=timezone.now(),
            **kwargs,
        )

    @classmethod
    def overdue(
        cls,
        **kwargs,
    ):
        return cls(
            status=UserTask.Status.OPEN,
            due_date=(
                timezone.localdate()
                - timedelta(days=1)
            ),
            **kwargs,
        )