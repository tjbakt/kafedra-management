from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.individual_plan.models import (
    IndividualPlanItem,
)
from apps.notifications.models import (
    Notification,
    UserTask,
)
from apps.notifications.services.notification_service import (
    NotificationService,
)


class Command(BaseCommand):
    help = (
        "Создаёт напоминания о приближающихся "
        "и просроченных пунктах индивидуального плана."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help=(
                "Количество дней до срока, "
                "за которое создаётся напоминание."
            ),
        )

    def handle(self, *args, **options):
        days = options["days"]
        today = timezone.localdate()
        deadline = today + timedelta(days=days)

        queryset = (
            IndividualPlanItem.objects
            .select_related(
                "individual_plan",
                "individual_plan__staff_employment",
                "individual_plan__staff_employment__staff_member",
            )
            .filter(
                is_archived=False,
                status__in=(
                    IndividualPlanItem.Status.PLANNED,
                    IndividualPlanItem.Status.IN_PROGRESS,
                ),
                planned_end_date__isnull=False,
                planned_end_date__lte=deadline,
            )
        )

        created_count = 0

        for item in queryset:
            teacher_user = (
                item.individual_plan
                .staff_employment
                .staff_member
                .user
            )

            if not teacher_user:
                continue

            is_overdue = item.planned_end_date < today

            if is_overdue:
                title = "Просрочен пункт индивидуального плана"
                description = (
                    f"Срок выполнения пункта "
                    f"«{item.title}» истёк "
                    f"{item.planned_end_date:%d.%m.%Y}."
                )
                priority = UserTask.Priority.URGENT
                notification_type = (
                    Notification.Type.WARNING
                )
                key_prefix = "overdue-plan-item"
            else:
                days_left = (
                    item.planned_end_date - today
                ).days

                title = "Приближается срок выполнения"
                description = (
                    f"До срока выполнения пункта "
                    f"«{item.title}» осталось "
                    f"{days_left} дн."
                )
                priority = UserTask.Priority.HIGH
                notification_type = (
                    Notification.Type.REMINDER
                )
                key_prefix = "deadline-plan-item"

            task, created = (
                NotificationService.create_task(
                    assignee=teacher_user,
                    task_type=(
                        UserTask.Type.DEADLINE_REMINDER
                    ),
                    title=title,
                    description=description,
                    priority=priority,
                    instance=item,
                    action_url=(
                        f"/individual-plans/"
                        f"{item.individual_plan_id}/items/"
                        f"{item.pk}"
                    ),
                    due_date=item.planned_end_date,
                    deduplication_key=(
                        f"{key_prefix}-{item.pk}-"
                        f"{item.planned_end_date}"
                    ),
                    metadata={
                        "planned_end_date": (
                            item.planned_end_date.isoformat()
                        ),
                        "is_overdue": is_overdue,
                    },
                    create_notification=False,
                )
            )

            if created:
                NotificationService.notify(
                    recipient=teacher_user,
                    title=title,
                    message=description,
                    notification_type=notification_type,
                    instance=item,
                    action_url=task.action_url,
                    metadata={
                        "task_id": task.pk,
                    },
                )
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Создано напоминаний: {created_count}"
            )
        )