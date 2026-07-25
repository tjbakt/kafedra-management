from django_filters import rest_framework as filters

from apps.notifications.models import (
    Notification,
    UserTask,
)

from django.utils import timezone


class NotificationFilter(filters.FilterSet):
    is_read = filters.BooleanFilter()
    is_archived = filters.BooleanFilter()
    notification_type = filters.ChoiceFilter(
        choices=Notification.Type.choices,
    )
    created_from = filters.IsoDateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )
    created_until = filters.IsoDateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )

    class Meta:
        model = Notification
        fields = (
            "notification_type",
            "is_read",
            "is_archived",
            "created_from",
            "created_until",
        )


class UserTaskFilter(filters.FilterSet):
    task_type = filters.ChoiceFilter(
        choices=UserTask.Type.choices,
    )
    status = filters.ChoiceFilter(
        choices=UserTask.Status.choices,
    )
    priority = filters.ChoiceFilter(
        choices=UserTask.Priority.choices,
    )
    due_from = filters.DateFilter(
        field_name="due_date",
        lookup_expr="gte",
    )
    due_until = filters.DateFilter(
        field_name="due_date",
        lookup_expr="lte",
    )
    overdue = filters.BooleanFilter(
        method="filter_overdue",
    )

    class Meta:
        model = UserTask
        fields = (
            "task_type",
            "status",
            "priority",
            "due_from",
            "due_until",
            "overdue",
        )

    def filter_overdue(
        self,
        queryset,
        name,
        value,
    ):
        if value is None:
            return queryset

        today = timezone.localdate()

        if value:
            return queryset.filter(
                status__in=(
                    UserTask.Status.OPEN,
                    UserTask.Status.IN_PROGRESS,
                ),
                due_date__lt=today,
            )

        return queryset.exclude(
            status__in=(
                UserTask.Status.OPEN,
                UserTask.Status.IN_PROGRESS,
            ),
            due_date__lt=today,
        )