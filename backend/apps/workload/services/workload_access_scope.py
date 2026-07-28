from dataclasses import dataclass

from apps.access_control.models import SystemRole
from apps.access_control.services.access_service import (
    AccessService,
)


@dataclass(frozen=True)
class WorkloadAccessScope:
    """
    Область данных нагрузки, доступная пользователю.

    Значение None означает отсутствие ограничения:
    пользователь имеет глобальный доступ.

    Пустое множество означает, что объекты этого типа
    пользователю недоступны.
    """

    department_ids: set[int] | None
    staff_member_ids: set[int] | None

    @property
    def has_global_access(self) -> bool:
        return (
            self.department_ids is None
            and self.staff_member_ids is None
        )

    @classmethod
    def for_user(cls, user) -> "WorkloadAccessScope":
        if user.is_superuser:
            return cls(
                department_ids=None,
                staff_member_ids=None,
            )

        if AccessService.has_global_role(
            user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.ACADEMIC_OFFICE,
        ):
            return cls(
                department_ids=None,
                staff_member_ids=None,
            )

        department_ids = (
            AccessService.accessible_department_ids(
                user,
                role_codes=(
                    SystemRole.Code.DEPARTMENT_HEAD,
                ),
            )
        )

        staff_member_ids = (
            AccessService.accessible_staff_member_ids(
                user
            )
        )

        return cls(
            department_ids=(
                set(department_ids)
                if department_ids is not None
                else None
            ),
            staff_member_ids=(
                set(staff_member_ids)
                if staff_member_ids is not None
                else None
            ),
        )

    def can_access_department(
        self,
        department_id,
    ) -> bool:
        if self.department_ids is None:
            return True

        try:
            normalized_id = int(department_id)
        except (TypeError, ValueError):
            return False

        return normalized_id in self.department_ids

    def can_access_staff_member(
        self,
        staff_member_id,
    ) -> bool:
        if self.staff_member_ids is None:
            return True

        try:
            normalized_id = int(staff_member_id)
        except (TypeError, ValueError):
            return False

        return normalized_id in self.staff_member_ids