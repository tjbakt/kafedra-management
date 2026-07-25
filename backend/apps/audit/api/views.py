from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.access_control.models import SystemRole
from apps.access_control.permissions import CanViewAuditLog
from apps.access_control.services.access_service import (
    AccessService,
)
from apps.audit.api.filters import AuditEventFilter
from apps.audit.api.serializers import AuditEventSerializer
from apps.audit.models import AuditEvent


class AuditEventViewSet(ReadOnlyModelViewSet):
    """
    Журнал доступен только для чтения.
    """

    serializer_class = AuditEventSerializer
    permission_classes = (
        IsAuthenticated,
        CanViewAuditLog,
    )
    filterset_class = AuditEventFilter
    search_fields = (
        "object_repr",
        "action_label",
        "reason",
        "actor_username",
        "actor_full_name",
    )
    ordering_fields = (
        "created_at",
        "action",
        "actor_username",
    )
    ordering = ("-created_at",)

    def get_queryset(self):
        queryset = AuditEvent.objects.select_related(
            "content_type",
            "actor",
        )

        user = self.request.user

        if user.is_superuser:
            return queryset

        if AccessService.has_global_role(
            user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.ACADEMIC_OFFICE,
        ):
            return queryset

        assignments = AccessService.active_assignments(user)

        filters = Q(pk__in=[])

        hr_global = assignments.filter(
            role__code=SystemRole.Code.HR_OFFICER,
            scope_type="global",
        ).exists()

        if hr_global:
            filters |= Q(
                content_type__app_label__in=(
                    "staff",
                    "access_control",
                )
            )

        university_ids = (
            AccessService.accessible_university_ids(user)
        )
        faculty_ids = (
            AccessService.accessible_faculty_ids(user)
        )
        department_ids = (
            AccessService.accessible_department_ids(user)
        )

        if university_ids:
            filters |= Q(
                university_id__in=university_ids
            )

        if faculty_ids:
            filters |= Q(
                faculty_id__in=faculty_ids
            )

        if department_ids:
            filters |= Q(
                department_id__in=department_ids
            )

        return queryset.filter(filters).distinct()

    @action(
        detail=False,
        methods=["get"],
        url_path="object-history",
    )
    def object_history(self, request):
        app_label = request.query_params.get(
            "app_label"
        )
        model = request.query_params.get(
            "model"
        )
        object_id = request.query_params.get(
            "object_id"
        )

        missing = []

        if not app_label:
            missing.append("app_label")

        if not model:
            missing.append("model")

        if not object_id:
            missing.append("object_id")

        if missing:
            return Response(
                {
                    "detail": (
                        "Необходимо указать: "
                        + ", ".join(missing)
                    )
                },
                status=400,
            )

        queryset = self.get_queryset().filter(
            content_type__app_label=app_label,
            content_type__model=model,
            object_id=str(object_id),
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