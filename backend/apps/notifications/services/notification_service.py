from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.notifications.models import (
    Notification,
    UserTask,
)


class NotificationService:
    @staticmethod
    def get_object_data(instance):
        if instance is None:
            return {
                "content_type": None,
                "object_id": None,
                "object_repr": "",
            }

        return {
            "content_type": ContentType.objects.get_for_model(
                instance,
                for_concrete_model=False,
            ),
            "object_id": str(instance.pk),
            "object_repr": str(instance)[:1000],
        }

    @classmethod
    def notify(
        cls,
        *,
        recipient,
        title,
        message,
        notification_type=Notification.Type.INFO,
        instance=None,
        action_url="",
        metadata=None,
    ):
        if recipient is None:
            return None

        object_data = cls.get_object_data(instance)

        return Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            action_url=action_url,
            metadata=metadata or {},
            **object_data,
        )

    @classmethod
    def notify_many(
        cls,
        *,
        recipients,
        title,
        message,
        notification_type=Notification.Type.INFO,
        instance=None,
        action_url="",
        metadata=None,
    ):
        object_data = cls.get_object_data(instance)

        unique_recipients = {
            recipient.pk: recipient
            for recipient in recipients
            if recipient is not None
        }

        notifications = [
            Notification(
                recipient=recipient,
                notification_type=notification_type,
                title=title,
                message=message,
                action_url=action_url,
                metadata=metadata or {},
                **object_data,
            )
            for recipient in unique_recipients.values()
        ]

        return Notification.objects.bulk_create(
            notifications
        )

    @classmethod
    @transaction.atomic
    def create_task(
        cls,
        *,
        assignee,
        task_type,
        title,
        description="",
        priority=UserTask.Priority.NORMAL,
        instance=None,
        action_url="",
        due_date=None,
        created_by=None,
        deduplication_key="",
        metadata=None,
        create_notification=True,
    ):
        object_data = cls.get_object_data(instance)

        defaults = {
            "task_type": task_type,
            "title": title,
            "description": description,
            "priority": priority,
            "action_url": action_url,
            "due_date": due_date,
            "created_by": created_by,
            "metadata": metadata or {},
            **object_data,
        }

        if deduplication_key:
            task = UserTask.objects.filter(
                assignee=assignee,
                deduplication_key=deduplication_key,
                status__in=(
                    UserTask.Status.OPEN,
                    UserTask.Status.IN_PROGRESS,
                ),
            ).first()

            if task:
                created = False
            else:
                task = UserTask.objects.create(
                    assignee=assignee,
                    deduplication_key=deduplication_key,
                    **defaults,
                )
                created = True
        else:
            task = UserTask.objects.create(
                assignee=assignee,
                **defaults,
            )
            created = True

        if created and create_notification:
            cls.notify(
                recipient=assignee,
                title=title,
                message=description or title,
                notification_type=(
                    Notification.Type.ACTION_REQUIRED
                ),
                instance=instance,
                action_url=action_url,
                metadata={
                    "task_id": task.pk,
                    "task_type": task.task_type,
                },
            )

        return task, created

    @staticmethod
    def start_task(*, task):
        if task.status != UserTask.Status.OPEN:
            return task

        task.status = UserTask.Status.IN_PROGRESS
        task.started_at = timezone.now()
        task.save(
            update_fields=(
                "status",
                "started_at",
                "updated_at",
            )
        )

        return task

    @staticmethod
    def complete_task(
        *,
        task,
        completion_comment="",
    ):
        if task.status in (
            UserTask.Status.COMPLETED,
            UserTask.Status.CANCELLED,
        ):
            return task

        task.status = UserTask.Status.COMPLETED
        task.completed_at = timezone.now()
        task.completion_comment = completion_comment
        task.save(
            update_fields=(
                "status",
                "completed_at",
                "completion_comment",
                "updated_at",
            )
        )

        return task

    @staticmethod
    def cancel_task(
        *,
        task,
        reason="",
    ):
        if task.status == UserTask.Status.COMPLETED:
            return task

        task.status = UserTask.Status.CANCELLED
        task.cancelled_at = timezone.now()
        task.cancellation_reason = reason
        task.save(
            update_fields=(
                "status",
                "cancelled_at",
                "cancellation_reason",
                "updated_at",
            )
        )

        return task

    @staticmethod
    def complete_tasks_for_object(
        *,
        instance,
        task_types=None,
        completion_comment="",
    ):
        content_type = ContentType.objects.get_for_model(
            instance,
            for_concrete_model=False,
        )

        queryset = UserTask.objects.filter(
            content_type=content_type,
            object_id=str(instance.pk),
            status__in=(
                UserTask.Status.OPEN,
                UserTask.Status.IN_PROGRESS,
            ),
        )

        if task_types:
            queryset = queryset.filter(
                task_type__in=task_types,
            )

        return queryset.update(
            status=UserTask.Status.COMPLETED,
            completed_at=timezone.now(),
            completion_comment=completion_comment,
            updated_at=timezone.now(),
        )