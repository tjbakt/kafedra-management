from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.access_control.models import SystemRole
from apps.access_control.services.access_service import (
    AccessService,
)


class IsSystemAdministrator(BasePermission):
    message = "Доступ разрешён только администратору системы."

    def has_permission(self, request, view):
        return AccessService.has_role(
            request.user,
            SystemRole.Code.SYSTEM_ADMIN,
        )


class IsAcademicOffice(BasePermission):
    message = "Доступ разрешён только учебному отделу."

    def has_permission(self, request, view):
        return AccessService.has_role(
            request.user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.ACADEMIC_OFFICE,
        )


class IsHROfficer(BasePermission):
    message = "Доступ разрешён кадровой службе."

    def has_permission(self, request, view):
        return AccessService.has_role(
            request.user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.HR_OFFICER,
        )


class IsDepartmentHead(BasePermission):
    message = "Доступ разрешён заведующему кафедрой."

    def has_permission(self, request, view):
        return AccessService.has_role(
            request.user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.DEPARTMENT_HEAD,
        )


class IsTeacher(BasePermission):
    message = "Доступ разрешён преподавателю."

    def has_permission(self, request, view):
        return AccessService.has_role(
            request.user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.TEACHER,
        )


class ReadOnlyOrAcademicManager(BasePermission):
    """
    Чтение доступно авторизованным пользователям.

    Изменение — администратору или учебному отделу.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return AccessService.has_role(
            request.user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.ACADEMIC_OFFICE,
        )

class CanManageWorkloadDistribution(BasePermission):
    message = (
        "У пользователя нет права распределять "
        "учебную нагрузку."
    )

    def has_permission(self, request, view):
        return AccessService.has_role(
            request.user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.ACADEMIC_OFFICE,
            SystemRole.Code.DEPARTMENT_HEAD,
        )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if AccessService.has_global_role(
            request.user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.ACADEMIC_OFFICE,
        ):
            return True

        department_id = (
            obj.planned_workload.teaching_department_id
        )

        return AccessService.can_manage_department(
            request.user,
            department_id,
        )

class CanEditIndividualPlan(BasePermission):
    message = (
        "У пользователя нет права изменять "
        "этот индивидуальный план."
    )

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if AccessService.has_global_role(
            request.user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.ACADEMIC_OFFICE,
        ):
            return True

        staff_member_id = (
            obj.staff_employment.staff_member_id
        )

        is_owner = AccessService.is_own_staff_member(
            request.user,
            staff_member_id,
        )

        if is_owner:
            return obj.status in (
                obj.Status.DRAFT,
                obj.Status.RETURNED,
            )

        return AccessService.can_manage_department(
            request.user,
            obj.staff_employment.department_id,
        )


class CanApproveIndividualPlan(BasePermission):
    message = (
        "У пользователя нет права утверждать "
        "этот индивидуальный план."
    )

    def has_permission(self, request, view):
        return AccessService.has_role(
            request.user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.ACADEMIC_OFFICE,
            SystemRole.Code.DEPARTMENT_HEAD,
        )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if AccessService.has_global_role(
            request.user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.ACADEMIC_OFFICE,
        ):
            return True

        return AccessService.can_manage_department(
            request.user,
            obj.staff_employment.department_id,
        )

class CanViewAuditLog(BasePermission):
    message = "У пользователя нет доступа к журналу аудита."

    def has_permission(self, request, view):
        return AccessService.has_role(
            request.user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.ACADEMIC_OFFICE,
            SystemRole.Code.HR_OFFICER,
            SystemRole.Code.DEAN_OFFICE,
            SystemRole.Code.DEPARTMENT_HEAD,
        )