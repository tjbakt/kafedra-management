from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.academics.models import AcademicYear
from apps.common.api.viewsets import BaseArchiveModelViewSet

from apps.workload.api.filters import (
    WorkloadDistributionFilter,
)
from apps.workload.api.serializers import (
    WorkloadDistributionSerializer,
    TeacherWorkloadSummarySerializer,
    DepartmentWorkloadSummarySerializer,
)
from apps.workload.models import WorkloadDistribution
from apps.workload.services.distribution_service import (
    WorkloadDistributionService,
)
from apps.workload.services.teacher_workload_service import (
    TeacherWorkloadService,
)
from apps.workload.services.department_workload_service import (
    DepartmentWorkloadService,
)

from apps.access_control.models import SystemRole
from apps.access_control.services.access_service import (
    AccessService,
)

from apps.access_control.permissions import (
    CanManageWorkloadDistribution,
)

from apps.workload.services.department_workload_export_service import (
    DepartmentWorkloadExportService,
)
from apps.workload.services.teacher_workload_export_service import (
    TeacherWorkloadExportService,
)
from apps.workload.services.workload_access_scope import (
    WorkloadAccessScope,
)


class WorkloadDistributionViewSet(
    BaseArchiveModelViewSet
):
    model = WorkloadDistribution
    serializer_class = WorkloadDistributionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = WorkloadDistributionFilter
    search_fields = (
        "staff_employment__staff_member__personnel_number",
        "staff_employment__staff_member__last_name",
        "staff_employment__staff_member__first_name",
        "staff_employment__staff_member__middle_name",
        "planned_workload__teaching_stream__code",
        "planned_workload__teaching_stream__name",
        "planned_workload__teaching_stream__"
        "curriculum_discipline__discipline__name_ru",
    )
    ordering_fields = (
        "allocated_hours",
        "created_at",
        "staff_employment__staff_member__last_name",
        "planned_workload__academic_year__start_year",
    )
    ordering = (
        "-planned_workload__academic_year__start_year",
        "staff_employment__staff_member__last_name",
    )

    def get_queryset(self):
        queryset = WorkloadDistribution.objects.select_related(
            "planned_workload",
            "planned_workload__academic_year",
            "planned_workload__academic_semester",
            "planned_workload__teaching_department",
            "planned_workload__teaching_stream",
            "planned_workload__teaching_stream__curriculum_discipline",
            "planned_workload__teaching_stream__curriculum_discipline__discipline",
            "planned_workload__curriculum_workload",
            "planned_workload__curriculum_workload__workload_type",
            "staff_employment",
            "staff_employment__staff_member",
            "staff_employment__position",
            "staff_employment__department",
            "approved_by",
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

        department_ids = (
            AccessService.accessible_department_ids(
                user,
                role_codes=(
                    SystemRole.Code.DEPARTMENT_HEAD,
                ),
            )
        )

        own_staff_ids = (
            AccessService.accessible_staff_member_ids(user)
        )

        if department_ids is None or own_staff_ids is None:
            return queryset

        return queryset.filter(
            Q(
                planned_workload__teaching_department_id__in=(
                    department_ids
                )
            )
            | Q(
                staff_employment__staff_member_id__in=(
                    own_staff_ids
                )
            )
        ).distinct()

    def perform_create(self, serializer):
        try:
            distribution = (
                WorkloadDistributionService
                .create_distribution(
                    planned_workload=(
                        serializer.validated_data[
                            "planned_workload"
                        ]
                    ),
                    staff_employment=(
                        serializer.validated_data[
                            "staff_employment"
                        ]
                    ),
                    allocated_hours=(
                        serializer.validated_data[
                            "allocated_hours"
                        ]
                    ),
                    notes=serializer.validated_data.get(
                        "notes",
                        "",
                    ),
                    user=self.request.user,
                )
            )
        except DjangoValidationError as exc:
            raise ValidationError(
                getattr(exc, "message_dict", exc.messages)
            ) from exc

        serializer.instance = distribution

    def perform_update(self, serializer):
        try:
            distribution = (
                WorkloadDistributionService
                .update_distribution(
                    distribution=self.get_object(),
                    staff_employment=(
                        serializer.validated_data.get(
                            "staff_employment"
                        )
                    ),
                    allocated_hours=(
                        serializer.validated_data.get(
                            "allocated_hours",
                            serializer.instance.allocated_hours,
                        )
                    ),
                    notes=serializer.validated_data.get(
                        "notes",
                        serializer.instance.notes,
                    ),
                    user=self.request.user,
                )
            )
        except DjangoValidationError as exc:
            raise ValidationError(
                getattr(exc, "message_dict", exc.messages)
            ) from exc

        serializer.instance = distribution

    @action(
        detail=True,
        methods=["post"],
        url_path="approve",
    )
    def approve(self, request, pk=None):
        distribution = self.get_object()

        try:
            distribution = (
                WorkloadDistributionService
                .approve_distribution(
                    distribution=distribution,
                    user=request.user,
                )
            )
        except DjangoValidationError as exc:
            raise ValidationError(
                getattr(exc, "message_dict", exc.messages)
            ) from exc

        serializer = self.get_serializer(distribution)

        return Response(
            {
                "detail": "Распределение утверждено.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="cancel",
    )
    def cancel(self, request, pk=None):
        distribution = self.get_object()

        reason = request.data.get(
            "reason",
            "",
        ).strip()

        if not reason:
            return Response(
                {
                    "reason": (
                        "Укажите причину отмены распределения."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        distribution = (
            WorkloadDistributionService
            .cancel_distribution(
                distribution=distribution,
                user=request.user,
                reason=reason,
            )
        )

        serializer = self.get_serializer(distribution)

        return Response(
            {
                "detail": "Распределение отменено.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="approve-selected",
    )
    def approve_selected(self, request):
        ids = request.data.get("ids", [])

        if not isinstance(ids, list) or not ids:
            return Response(
                {
                    "detail": (
                        "Необходимо передать непустой список ids."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(
            id__in=ids
        )

        approved_ids = []
        errors = []

        with transaction.atomic():
            for distribution in queryset:
                try:
                    approved = (
                        WorkloadDistributionService
                        .approve_distribution(
                            distribution=distribution,
                            user=request.user,
                        )
                    )
                    approved_ids.append(approved.id)
                except DjangoValidationError as exc:
                    errors.append(
                        {
                            "id": distribution.id,
                            "error": (
                                getattr(
                                    exc,
                                    "message_dict",
                                    exc.messages,
                                )
                            ),
                        }
                    )

        return Response(
            {
                "approved_count": len(approved_ids),
                "approved_ids": approved_ids,
                "errors_count": len(errors),
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="teacher-summary",
    )
    def teacher_summary(self, request):
        academic_year_id = request.query_params.get(
            "academic_year"
        )
        staff_member_id = request.query_params.get(
            "staff_member"
        )
        department_id = request.query_params.get(
            "department"
        )

        if not academic_year_id:
            return Response(
                {
                    "detail": (
                        "Необходимо указать academic_year."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            academic_year = AcademicYear.objects.get(
                pk=academic_year_id
            )
        except AcademicYear.DoesNotExist:
            return Response(
                {
                    "academic_year": (
                        "Указанный учебный год не найден."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        access_scope = self.get_workload_access_scope()
        result = TeacherWorkloadService.get_summary(
            academic_year=academic_year,
            staff_member_id=staff_member_id,
            department_id=department_id,
            allowed_department_ids=(
                access_scope.department_ids
            ),
            allowed_staff_member_ids=(
                access_scope.staff_member_ids
            ),
        )

        serializer = TeacherWorkloadSummarySerializer(
            result,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="teacher-summary/export",
    )
    def export_teacher_summary(self, request):
        academic_year_id = request.query_params.get(
            "academic_year"
        )
        staff_member_id = request.query_params.get(
            "staff_member"
        )
        department_id = request.query_params.get(
            "department"
        )

        if not academic_year_id:
            return Response(
                {
                    "academic_year": (
                        "Необходимо указать учебный год."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            academic_year = AcademicYear.objects.get(
                pk=academic_year_id,
            )
        except (
                AcademicYear.DoesNotExist,
                ValueError,
                TypeError,
        ):
            return Response(
                {
                    "academic_year": (
                        "Указан некорректный учебный год."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            file_content, filename = (
                TeacherWorkloadExportService.export(
                    academic_year=academic_year,
                    staff_member_id=staff_member_id,
                    department_id=department_id,
                )
            )
        except (ValueError, TypeError):
            return Response(
                {
                    "detail": (
                        "Некорректные параметры экспорта."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_scope = self.get_workload_access_scope()
        response = HttpResponse(
            file_content, filename=(
                TeacherWorkloadExportService.export(
                    academic_year=academic_year,
                    staff_member_id=staff_member_id,
                    department_id=department_id,
                    allowed_department_ids=(
                        access_scope.department_ids
                    ),
                    allowed_staff_member_ids=(
                        access_scope.staff_member_ids
                    ),
                )
            )
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )
        response["Content-Length"] = len(file_content)

        return response

    @action(
        detail=False,
        methods=["get"],
        url_path="department-summary",
    )
    def department_summary(self, request):
        academic_year_id = request.query_params.get(
            "academic_year"
        )
        academic_semester_id = request.query_params.get(
            "academic_semester"
        )
        department_id = request.query_params.get(
            "department"
        )

        if not academic_year_id:
            return Response(
                {
                    "academic_year": (
                        "Необходимо указать учебный год."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            academic_year = AcademicYear.objects.get(
                pk=academic_year_id,
            )
        except AcademicYear.DoesNotExist:
            return Response(
                {
                    "academic_year": (
                        "Указанный учебный год не найден."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        access_scope = self.get_workload_access_scope()

        self.validate_department_access(
            access_scope=access_scope,
            department_id=department_id,
        )

        result = DepartmentWorkloadService.get_summary(
            academic_year=academic_year,
            academic_semester_id=academic_semester_id,
            department_id=department_id,
            allowed_department_ids=(
                access_scope.department_ids
            ),
        )

        serializer = DepartmentWorkloadSummarySerializer(
            result,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="department-summary/export",
    )
    def export_department_summary(self, request):
        academic_year_id = request.query_params.get(
            "academic_year"
        )
        academic_semester_id = request.query_params.get(
            "academic_semester"
        )
        department_id = request.query_params.get(
            "department"
        )

        if not academic_year_id:
            return Response(
                {
                    "academic_year": (
                        "Необходимо указать учебный год."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            academic_year = AcademicYear.objects.get(
                pk=academic_year_id,
            )
        except (
                AcademicYear.DoesNotExist,
                ValueError,
                TypeError,
        ):
            return Response(
                {
                    "academic_year": (
                        "Указан некорректный учебный год."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            file_content, filename = (
                DepartmentWorkloadExportService.export(
                    academic_year=academic_year,
                    academic_semester_id=(
                        academic_semester_id
                    ),
                    department_id=department_id,
                )
            )
        except (ValueError, TypeError):
            return Response(
                {
                    "detail": (
                        "Некорректные параметры экспорта."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_scope = self.get_workload_access_scope()

        self.validate_department_access(
            access_scope=access_scope,
            department_id=department_id,
        )

        response = HttpResponse(
            file_content, filename=(
                DepartmentWorkloadExportService.export(
                    academic_year=academic_year,
                    academic_semester_id=(
                        academic_semester_id
                    ),
                    department_id=department_id,
                    allowed_department_ids=(
                        access_scope.department_ids
                    ),
                )
            )
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )
        response["Content-Length"] = len(file_content)

        return response

    def get_permissions(self):
        if self.action in (
                "create",
                "update",
                "partial_update",
                "destroy",
                "approve",
                "cancel",
                "approve_selected",
        ):
            permission_classes = [
                IsAuthenticated,
                CanManageWorkloadDistribution,
            ]
        else:
            permission_classes = [
                IsAuthenticated,
            ]

        return [
            permission()
            for permission in permission_classes
        ]

    def get_workload_access_scope(self):
        return WorkloadAccessScope.for_user(
            self.request.user
        )

    @staticmethod
    def validate_department_access(
            *,
            access_scope,
            department_id,
    ):
        if (
                department_id
                and not access_scope.can_access_department(
            department_id
        )
        ):
            raise PermissionDenied(
                "У вас нет доступа к указанной кафедре."
            )