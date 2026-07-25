from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.access_control.api.filters import (
    SystemRoleFilter,
    UserRoleAssignmentFilter,
)
from apps.access_control.api.serializers import (
    SystemRoleSerializer,
    UserRoleAssignmentSerializer,
)
from apps.access_control.models import (
    SystemRole,
    UserRoleAssignment,
)
from apps.access_control.permissions import (
    IsSystemAdministrator,
)
from apps.access_control.services.access_service import (
    AccessService,
)
from apps.common.api.viewsets import BaseArchiveModelViewSet

from apps.audit.models import AuditEvent
from apps.audit.services.audit_service import AuditService


class SystemRoleViewSet(BaseArchiveModelViewSet):
    model = SystemRole
    queryset = SystemRole.objects.all()
    serializer_class = SystemRoleSerializer
    permission_classes = (
        IsAuthenticated,
        IsSystemAdministrator,
    )
    filterset_class = SystemRoleFilter
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
    )
    ordering = (
        "sort_order",
        "name_ru",
    )


class UserRoleAssignmentViewSet(
    BaseArchiveModelViewSet
):
    model = UserRoleAssignment
    serializer_class = UserRoleAssignmentSerializer
    permission_classes = (
        IsAuthenticated,
        IsSystemAdministrator,
    )
    filterset_class = UserRoleAssignmentFilter
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "role__name_ru",
        "department__name_ru",
        "faculty__name_ru",
        "staff_member__last_name",
    )
    ordering = (
        "user__username",
        "role__sort_order",
    )

    def get_queryset(self):
        return UserRoleAssignment.objects.select_related(
            "user",
            "role",
            "university",
            "faculty",
            "department",
            "department__faculty",
            "staff_member",
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="my-access",
        permission_classes=[IsAuthenticated],
    )
    def my_access(self, request):
        assignments = AccessService.active_assignments(
            request.user
        )

        serializer = self.get_serializer(
            assignments,
            many=True,
        )

        return Response(
            {
                "user": request.user.id,
                "username": request.user.username,
                "is_superuser": request.user.is_superuser,
                "roles": serializer.data,
            }
        )

    def perform_create(self, serializer):
        assignment = serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

        AuditService.log(
            instance=assignment,
            action=AuditEvent.Action.CREATE,
            actor=self.request.user,
            action_label="Пользователю назначена системная роль",
            new_values={
                "user": assignment.user_id,
                "role": assignment.role_id,
                "role_code": assignment.role.code,
                "scope_type": assignment.scope_type,
                "university": assignment.university_id,
                "faculty": assignment.faculty_id,
                "department": assignment.department_id,
                "staff_member": assignment.staff_member_id,
                "valid_from": assignment.valid_from,
                "valid_until": assignment.valid_until,
                "is_active": assignment.is_active,
            },
            changed_fields=[
                "user",
                "role",
                "scope_type",
                "university",
                "faculty",
                "department",
                "staff_member",
                "valid_from",
                "valid_until",
                "is_active",
            ],
        )

    def perform_update(self, serializer):
        instance = self.get_object()

        old_values = {
            "role": instance.role_id,
            "scope_type": instance.scope_type,
            "university": instance.university_id,
            "faculty": instance.faculty_id,
            "department": instance.department_id,
            "staff_member": instance.staff_member_id,
            "valid_from": instance.valid_from,
            "valid_until": instance.valid_until,
            "is_active": instance.is_active,
        }

        assignment = serializer.save(
            updated_by=self.request.user,
        )

        new_values = {
            "role": assignment.role_id,
            "scope_type": assignment.scope_type,
            "university": assignment.university_id,
            "faculty": assignment.faculty_id,
            "department": assignment.department_id,
            "staff_member": assignment.staff_member_id,
            "valid_from": assignment.valid_from,
            "valid_until": assignment.valid_until,
            "is_active": assignment.is_active,
        }

        changed_fields = [
            field_name
            for field_name in old_values
            if old_values[field_name]
               != new_values[field_name]
        ]

        AuditService.log(
            instance=assignment,
            action=AuditEvent.Action.UPDATE,
            actor=self.request.user,
            action_label="Изменено назначение системной роли",
            old_values=old_values,
            new_values=new_values,
            changed_fields=changed_fields,
        )