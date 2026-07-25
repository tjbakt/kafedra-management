from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.notifications.api.filters import (
    NotificationFilter,
    UserTaskFilter,
)
from apps.notifications.api.serializers import (
    NotificationSerializer,
    UserTaskSerializer,
)
from apps.notifications.models import (
    Notification,
    UserTask,
)
from apps.notifications.services.notification_service import (
    NotificationService,
)

class NotificationViewSet(ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = NotificationFilter
    search_fields = (
        "title",
        "message",
        "object_repr",
    )
    ordering_fields = (
        "created_at",
        "is_read",
        "notification_type",
    )
    ordering = ("-created_at",)

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user,
        ).select_related(
            "content_type",
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="mark-read",
    )
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.mark_as_read()

        return Response(
            self.get_serializer(notification).data
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="mark-all-read",
    )
    def mark_all_read(self, request):
        updated = self.get_queryset().filter(
            is_read=False,
            is_archived=False,
        ).update(
            is_read=True,
            read_at=timezone.now(),
        )

        return Response(
            {
                "detail": "Все уведомления отмечены прочитанными.",
                "updated_count": updated,
            }
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="archive",
    )
    def archive(self, request, pk=None):
        notification = self.get_object()
        notification.archive()

        return Response(
            self.get_serializer(notification).data
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="unread-count",
    )
    def unread_count(self, request):
        count = self.get_queryset().filter(
            is_read=False,
            is_archived=False,
        ).count()

        return Response(
            {
                "unread_count": count,
            }
        )

class UserTaskViewSet(ReadOnlyModelViewSet):
    serializer_class = UserTaskSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = UserTaskFilter
    search_fields = (
        "title",
        "description",
        "object_repr",
        "completion_comment",
    )
    ordering_fields = (
        "created_at",
        "due_date",
        "priority",
        "status",
    )
    ordering = (
        "due_date",
        "-priority",
        "-created_at",
    )

    def get_queryset(self):
        return UserTask.objects.filter(
            assignee=self.request.user,
        ).select_related(
            "content_type",
            "assignee",
            "created_by",
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="start",
    )
    def start(self, request, pk=None):
        task = self.get_object()

        if task.status != UserTask.Status.OPEN:
            return Response(
                {
                    "detail": (
                        "Начать можно только открытую задачу."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = NotificationService.start_task(
            task=task
        )

        return Response(
            self.get_serializer(task).data
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="complete",
    )
    def complete(self, request, pk=None):
        task = self.get_object()

        if task.status not in (
            UserTask.Status.OPEN,
            UserTask.Status.IN_PROGRESS,
        ):
            return Response(
                {
                    "detail": (
                        "Эту задачу нельзя отметить выполненной."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = NotificationService.complete_task(
            task=task,
            completion_comment=request.data.get(
                "completion_comment",
                "",
            ),
        )

        return Response(
            self.get_serializer(task).data
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="summary",
    )
    def summary(self, request):
        queryset = self.get_queryset()
        today = timezone.localdate()

        by_status = {
            item["status"]: item["count"]
            for item in queryset.values(
                "status"
            ).annotate(
                count=Count("id")
            )
        }

        overdue_count = queryset.filter(
            status__in=(
                UserTask.Status.OPEN,
                UserTask.Status.IN_PROGRESS,
            ),
            due_date__lt=today,
        ).count()

        due_today_count = queryset.filter(
            status__in=(
                UserTask.Status.OPEN,
                UserTask.Status.IN_PROGRESS,
            ),
            due_date=today,
        ).count()

        return Response(
            {
                "open": by_status.get(
                    UserTask.Status.OPEN,
                    0,
                ),
                "in_progress": by_status.get(
                    UserTask.Status.IN_PROGRESS,
                    0,
                ),
                "completed": by_status.get(
                    UserTask.Status.COMPLETED,
                    0,
                ),
                "cancelled": by_status.get(
                    UserTask.Status.CANCELLED,
                    0,
                ),
                "expired": by_status.get(
                    UserTask.Status.EXPIRED,
                    0,
                ),
                "overdue": overdue_count,
                "due_today": due_today_count,
            }
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="inbox",
    )
    def inbox(self, request):
        queryset = self.get_queryset().filter(
            status__in=(
                UserTask.Status.OPEN,
                UserTask.Status.IN_PROGRESS,
            )
        )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )
            return self.get_paginated_response(
                serializer.data
            )

        return Response(
            self.get_serializer(
                queryset,
                many=True,
            ).data
        )