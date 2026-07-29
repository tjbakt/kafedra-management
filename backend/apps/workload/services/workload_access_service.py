from rest_framework.exceptions import PermissionDenied

from apps.access_control.models import SystemRole
from apps.access_control.services.access_service import (
    AccessService,
)


class WorkloadAccessService:
    """
    Общие правила ограничения данных workload
    доступными пользователю кафедрами.
    """

    @classmethod
    def resolve_validation_department_ids(
        cls,
        *,
        user,
        requested_department_id=None,
    ):
        if AccessService.has_global_role(
            user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.ACADEMIC_OFFICE,
        ):
            if requested_department_id is None:
                return None

            return {
                requested_department_id,
            }

        accessible_department_ids = (
            AccessService.accessible_department_ids(
                user,
                role_codes=(
                    SystemRole.Code.DEPARTMENT_HEAD,
                ),
            )
        )

        if accessible_department_ids is None:
            if requested_department_id is None:
                return None

            return {
                requested_department_id,
            }

        accessible_department_ids = set(
            accessible_department_ids
        )

        if requested_department_id is not None:
            if (
                requested_department_id
                not in accessible_department_ids
            ):
                raise PermissionDenied(
                    "У пользователя нет доступа "
                    "к указанной кафедре."
                )

            return {
                requested_department_id,
            }

        return accessible_department_ids