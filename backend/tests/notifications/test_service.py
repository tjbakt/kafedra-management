from django.test import TestCase

from apps.notifications.models import (
    Notification,
    UserTask,
)
from apps.notifications.services.notification_service import (
    NotificationService,
)
from tests.factories import (
    DepartmentFactory,
    UserFactory,
    UserTaskFactory,
)


class NotificationServiceTests(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_notify(self):
        department = DepartmentFactory()

        notification = (
            NotificationService.notify(
                recipient=self.user,
                title="Изменение кафедры",
                message="Карточка обновлена.",
                notification_type=(
                    Notification.Type.SUCCESS
                ),
                instance=department,
                action_url=(
                    f"/departments/{department.pk}"
                ),
                metadata={
                    "source": "test",
                },
            )
        )

        self.assertEqual(
            notification.recipient,
            self.user,
        )
        self.assertEqual(
            notification.object_id,
            str(department.pk),
        )
        self.assertEqual(
            notification.content_object,
            department,
        )
        self.assertEqual(
            notification.metadata["source"],
            "test",
        )

    def test_notify_none_recipient(self):
        result = NotificationService.notify(
            recipient=None,
            title="Тест",
            message="Тест",
        )

        self.assertIsNone(result)

    def test_notify_many_removes_duplicates(
        self,
    ):
        second_user = UserFactory()

        result = NotificationService.notify_many(
            recipients=[
                self.user,
                self.user,
                second_user,
                None,
            ],
            title="Массовое уведомление",
            message="Сообщение",
        )

        self.assertEqual(len(result), 2)

        recipient_ids = {
            item.recipient_id
            for item in result
        }

        self.assertEqual(
            recipient_ids,
            {
                self.user.pk,
                second_user.pk,
            },
        )

    def test_create_task_and_notification(
        self,
    ):
        task, created = (
            NotificationService.create_task(
                assignee=self.user,
                task_type=(
                    UserTask.Type
                    .APPROVE_INDIVIDUAL_PLAN
                ),
                title="Утвердить план",
                description=(
                    "Проверьте индивидуальный план."
                ),
                created_by=UserFactory(),
                deduplication_key=(
                    "approve-plan-1"
                ),
            )
        )

        self.assertTrue(created)
        self.assertEqual(
            task.assignee,
            self.user,
        )

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.user,
                notification_type=(
                    Notification.Type
                    .ACTION_REQUIRED
                ),
                metadata__task_id=task.pk,
            ).exists()
        )

    def test_create_task_is_idempotent(
        self,
    ):
        first, first_created = (
            NotificationService.create_task(
                assignee=self.user,
                task_type=UserTask.Type.OTHER,
                title="Одинаковая задача",
                deduplication_key="same-task",
                create_notification=False,
            )
        )

        second, second_created = (
            NotificationService.create_task(
                assignee=self.user,
                task_type=UserTask.Type.OTHER,
                title="Одинаковая задача",
                deduplication_key="same-task",
                create_notification=False,
            )
        )

        self.assertTrue(first_created)
        self.assertFalse(second_created)
        self.assertEqual(first.pk, second.pk)

    def test_start_task(self):
        task = UserTaskFactory(
            status=UserTask.Status.OPEN,
        )

        result = NotificationService.start_task(
            task=task
        )

        result.refresh_from_db()

        self.assertEqual(
            result.status,
            UserTask.Status.IN_PROGRESS,
        )
        self.assertIsNotNone(
            result.started_at
        )

    def test_complete_task(self):
        task = UserTaskFactory.in_progress()

        result = (
            NotificationService.complete_task(
                task=task,
                completion_comment=(
                    "Задача выполнена."
                ),
            )
        )

        result.refresh_from_db()

        self.assertEqual(
            result.status,
            UserTask.Status.COMPLETED,
        )
        self.assertIsNotNone(
            result.completed_at
        )
        self.assertEqual(
            result.completion_comment,
            "Задача выполнена.",
        )

    def test_cancel_task(self):
        task = UserTaskFactory()

        result = (
            NotificationService.cancel_task(
                task=task,
                reason="Задача неактуальна.",
            )
        )

        result.refresh_from_db()

        self.assertEqual(
            result.status,
            UserTask.Status.CANCELLED,
        )
        self.assertIsNotNone(
            result.cancelled_at
        )
        self.assertEqual(
            result.cancellation_reason,
            "Задача неактуальна.",
        )

    def test_complete_tasks_for_object(self):
        department = DepartmentFactory()

        first, _ = NotificationService.create_task(
            assignee=self.user,
            task_type=UserTask.Type.OTHER,
            title="Первая задача",
            instance=department,
            create_notification=False,
        )
        second, _ = NotificationService.create_task(
            assignee=self.user,
            task_type=UserTask.Type.OTHER,
            title="Вторая задача",
            instance=department,
            create_notification=False,
        )

        updated = (
            NotificationService
            .complete_tasks_for_object(
                instance=department,
                completion_comment=(
                    "Объект обработан."
                ),
            )
        )

        self.assertEqual(updated, 2)

        first.refresh_from_db()
        second.refresh_from_db()

        self.assertEqual(
            first.status,
            UserTask.Status.COMPLETED,
        )
        self.assertEqual(
            second.status,
            UserTask.Status.COMPLETED,
        )