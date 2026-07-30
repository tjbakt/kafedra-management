from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, FileResponse

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.academics.models import AcademicYear
from apps.common.api.viewsets import BaseArchiveModelViewSet

from apps.workload.api.filters import (
    WorkloadDistributionFilter,
)
from apps.workload.api.serializers import (
    WorkloadDistributionSerializer,
    TeacherWorkloadSummarySerializer,
    DepartmentWorkloadSummarySerializer,
    WorkloadDashboardSerializer,
    CancelSelectedDistributionsResultSerializer,
    CancelSelectedDistributionsSerializer,
    RestoreDistributionSerializer,
    RestoreSelectedDistributionsResultSerializer,
    RestoreSelectedDistributionsSerializer,
    TransferDistributionHoursResultSerializer,
    TransferDistributionHoursSerializer,
    ReturnDistributionToDraftSerializer,
    ReturnSelectedToDraftResultSerializer,
    ReturnSelectedToDraftSerializer,
    DistributionAvailableActionsSerializer,
    AcademicYearValidationQuerySerializer,
    AcademicYearValidationResultSerializer,
    AcademicYearClosingReadinessQuerySerializer,
    AcademicYearClosingReadinessResultSerializer,
    CancelDistributionSerializer,
    TransferDistributionActionResponseSerializer,
    WorkloadDistributionActionResponseSerializer,
    ApproveSelectedDistributionsResultSerializer,
    ApproveSelectedDistributionsSerializer,
    DepartmentWorkloadSummaryQuerySerializer,
    TeacherWorkloadSummaryQuerySerializer,
    WorkloadDashboardQuerySerializer,
)
from apps.workload.models import WorkloadDistribution

from apps.access_control.models import SystemRole
from apps.access_control.services.access_service import (
    AccessService,
)
from apps.access_control.permissions import (
    CanManageWorkloadDistribution,
    CanValidateAcademicYearWorkload,
    CanCheckAcademicYearClosingReadiness,
)

from apps.workload.services.distribution_service import (
    WorkloadDistributionService,
)
from apps.workload.services.teacher_workload_service import (
    TeacherWorkloadService,
)
from apps.workload.services.department_workload_service import (
    DepartmentWorkloadService,
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
from apps.workload.services.workload_dashboard_service import (
    WorkloadDashboardService,
)
from apps.workload.services.workload_dashboard_export_service import (
    WorkloadDashboardExportService,
)
from apps.workload.services.academic_year_validation_service import (
    AcademicYearWorkloadValidationService,
)
from apps.workload.services.workload_access_service import (
    WorkloadAccessService,
)
from apps.workload.services.academic_year_validation_excel_service import (
    AcademicYearValidationExcelService,
)
from apps.workload.services.academic_year_closing_readiness_service import (
    AcademicYearClosingReadinessService,
)

from apps.staff.models import StaffEmployment
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
)
from apps.common.api.schema import (
    BAD_REQUEST_RESPONSE,
    FORBIDDEN_RESPONSE,
    NOT_FOUND_RESPONSE,
    UNAUTHORIZED_RESPONSE,
    CONFLICT_RESPONSE,
)
from apps.workload.api.schema_serializers import (
    AcademicYearClosingReadinessResponseSerializer,
    AcademicYearWorkloadValidationResponseSerializer,
)


EXCEL_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument."
    "spreadsheetml.sheet"
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

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary=(
                "Вернуть распределение в черновик"
        ),
        description=(
                "Возвращает утверждённое или отменённое "
                "распределение нагрузки в статус черновика. "
                "Необходимо указать причину возврата."
        ),
        request=ReturnDistributionToDraftSerializer,
        responses={
            200: (
                    WorkloadDistributionActionResponseSerializer
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
            409: CONFLICT_RESPONSE,
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="return-to-draft",
    )
    def return_to_draft(self, request, pk=None):
        input_serializer = (
            ReturnDistributionToDraftSerializer(
                data=request.data
            )
        )
        input_serializer.is_valid(
            raise_exception=True
        )

        distribution = self.get_object()

        try:
            distribution = (
                WorkloadDistributionService
                .return_distribution_to_draft(
                    distribution=distribution,
                    user=request.user,
                    reason=(
                        input_serializer.validated_data[
                            "reason"
                        ]
                    ),
                )
            )
        except DjangoValidationError as exc:
            raise ValidationError(
                getattr(
                    exc,
                    "message_dict",
                    exc.messages,
                )
            ) from exc

        output_serializer = self.get_serializer(
            distribution
        )

        return Response(
            {
                "detail": (
                    "Распределение возвращено "
                    "в статус черновика."
                ),
                "data": output_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary="Утвердить распределение",
        description=(
                "Переводит распределение учебной нагрузки "
                "из статуса черновика в утверждённое "
                "состояние."
        ),
        request=None,
        responses={
            200: (
                    WorkloadDistributionActionResponseSerializer
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
            409: CONFLICT_RESPONSE,
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="approve",
    )
    def approve(
            self,
            request,
            pk=None,
    ):
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
                getattr(
                    exc,
                    "message_dict",
                    exc.messages,
                )
            ) from exc

        serializer = self.get_serializer(
            distribution
        )

        return Response(
            {
                "detail": (
                    "Распределение утверждено."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary="Отменить распределение",
        description=(
                "Отменяет существующее распределение "
                "учебной нагрузки. Причина отмены "
                "обязательна."
        ),
        request=CancelDistributionSerializer,
        responses={
            200: (
                    WorkloadDistributionActionResponseSerializer
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
            409: CONFLICT_RESPONSE,
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="cancel",
    )
    def cancel(
            self,
            request,
            pk=None,
    ):
        input_serializer = CancelDistributionSerializer(
            data=request.data
        )
        input_serializer.is_valid(
            raise_exception=True
        )

        distribution = self.get_object()

        try:
            distribution = (
                WorkloadDistributionService
                .cancel_distribution(
                    distribution=distribution,
                    user=request.user,
                    reason=(
                        input_serializer.validated_data[
                            "reason"
                        ]
                    ),
                )
            )
        except DjangoValidationError as exc:
            raise ValidationError(
                getattr(
                    exc,
                    "message_dict",
                    exc.messages,
                )
            ) from exc

        output_serializer = self.get_serializer(
            distribution
        )

        return Response(
            {
                "detail": (
                    "Распределение отменено."
                ),
                "data": output_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary="Перенести часы нагрузки",
        description=(
                "Переносит указанное количество часов "
                "из текущего распределения на другое "
                "трудовое назначение преподавателя."
        ),
        request=TransferDistributionHoursSerializer,
        responses={
            200: (
                    TransferDistributionActionResponseSerializer
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
            409: CONFLICT_RESPONSE,
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="transfer",
    )
    def transfer(
            self,
            request,
            pk=None,
    ):
        input_serializer = (
            TransferDistributionHoursSerializer(
                data=request.data
            )
        )
        input_serializer.is_valid(
            raise_exception=True
        )

        source_distribution = self.get_object()

        target_staff_employment_id = (
            input_serializer.validated_data[
                "target_staff_employment"
            ]
        )

        try:
            target_staff_employment = (
                StaffEmployment.objects
                .select_related(
                    "staff_member",
                    "department",
                    "position",
                )
                .get(
                    pk=target_staff_employment_id,
                    is_archived=False,
                )
            )
        except StaffEmployment.DoesNotExist as exc:
            raise ValidationError(
                {
                    "target_staff_employment": (
                        "Указанное трудовое назначение "
                        "не найдено."
                    )
                }
            ) from exc

        try:
            result = (
                WorkloadDistributionService
                .transfer_distribution_hours(
                    source_distribution=(
                        source_distribution
                    ),
                    target_staff_employment=(
                        target_staff_employment
                    ),
                    transfer_hours=(
                        input_serializer.validated_data[
                            "transfer_hours"
                        ]
                    ),
                    user=request.user,
                    reason=(
                        input_serializer.validated_data[
                            "reason"
                        ]
                    ),
                )
            )
        except DjangoValidationError as exc:
            raise ValidationError(
                getattr(
                    exc,
                    "message_dict",
                    exc.messages,
                )
            ) from exc

        output_serializer = (
            TransferDistributionHoursResultSerializer(
                result
            )
        )

        return Response(
            {
                "detail": (
                    "Часы нагрузки успешно перенесены."
                ),
                "data": output_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary="Восстановить распределение",
        description=(
                "Восстанавливает отменённое распределение "
                "и переводит его в статус черновика."
        ),
        request=RestoreDistributionSerializer,
        responses={
            200: (
                    WorkloadDistributionActionResponseSerializer
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
            409: CONFLICT_RESPONSE,
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
    )
    def restore(
            self,
            request,
            pk=None,
    ):
        input_serializer = RestoreDistributionSerializer(
            data=request.data
        )
        input_serializer.is_valid(
            raise_exception=True
        )

        distribution = self.get_object()

        try:
            distribution = (
                WorkloadDistributionService
                .restore_distribution(
                    distribution=distribution,
                    user=request.user,
                    reason=(
                        input_serializer.validated_data[
                            "reason"
                        ]
                    ),
                )
            )
        except DjangoValidationError as exc:
            raise ValidationError(
                getattr(
                    exc,
                    "message_dict",
                    exc.messages,
                )
            ) from exc

        output_serializer = self.get_serializer(
            distribution
        )

        return Response(
            {
                "detail": (
                    "Распределение восстановлено "
                    "в статусе черновика."
                ),
                "data": output_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary="Получить доступные действия",
        description=(
                "Возвращает перечень операций, доступных "
                "для распределения в его текущем состоянии, "
                "и причины недоступности остальных операций."
        ),
        request=None,
        responses={
            200: DistributionAvailableActionsSerializer,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="available-actions",
    )
    def available_actions(
        self,
        request,
        pk=None,
    ):
        distribution = self.get_object()

        result = (
            WorkloadDistributionService
            .get_available_actions(
                distribution=distribution
            )
        )

        serializer = (
            DistributionAvailableActionsSerializer(
                result
            )
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary=(
                "Массово утвердить распределения"
        ),
        description=(
                "Утверждает доступные распределения "
                "нагрузки из переданного списка ID. "
                "Распределения, недоступные текущему "
                "пользователю, возвращаются в поле "
                "unavailable_ids. Ошибка одного объекта "
                "не отменяет обработку остальных."
        ),
        request=(
                ApproveSelectedDistributionsSerializer
        ),
        responses={
            200: (
                    ApproveSelectedDistributionsResultSerializer
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            409: CONFLICT_RESPONSE,
        },
        examples=[
            OpenApiExample(
                name="Массовое утверждение",
                value={
                    "ids": [
                        12,
                        13,
                        14,
                    ],
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Результат утверждения",
                value={
                    "requested_count": 3,
                    "found_count": 2,
                    "approved_count": 1,
                    "approved_ids": [
                        12,
                    ],
                    "unavailable_count": 1,
                    "unavailable_ids": [
                        14,
                    ],
                    "errors_count": 1,
                    "errors": [
                        {
                            "id": 13,
                            "error": [
                                (
                                        "Распределение уже "
                                        "утверждено."
                                )
                            ],
                        }
                    ],
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="approve-selected",
    )
    def approve_selected(
            self,
            request,
    ):
        input_serializer = (
            ApproveSelectedDistributionsSerializer(
                data=request.data
            )
        )
        input_serializer.is_valid(
            raise_exception=True
        )

        requested_ids = (
            input_serializer.validated_data["ids"]
        )

        distributions = list(
            self.get_queryset()
            .filter(
                pk__in=requested_ids
            )
            .order_by("pk")
        )

        found_ids = {
            distribution.pk
            for distribution in distributions
        }

        unavailable_ids = [
            distribution_id
            for distribution_id in requested_ids
            if distribution_id not in found_ids
        ]

        approved_ids = []
        errors = []

        with transaction.atomic():
            for distribution in distributions:
                try:
                    approved = (
                        WorkloadDistributionService
                        .approve_distribution(
                            distribution=distribution,
                            user=request.user,
                        )
                    )
                    approved_ids.append(
                        approved.pk
                    )
                except DjangoValidationError as exc:
                    errors.append(
                        {
                            "id": distribution.pk,
                            "error": getattr(
                                exc,
                                "message_dict",
                                exc.messages,
                            ),
                        }
                    )

        result = {
            "requested_count": len(
                requested_ids
            ),
            "found_count": len(
                distributions
            ),
            "approved_count": len(
                approved_ids
            ),
            "approved_ids": approved_ids,
            "unavailable_count": len(
                unavailable_ids
            ),
            "unavailable_ids": (
                unavailable_ids
            ),
            "errors_count": len(errors),
            "errors": errors,
        }

        output_serializer = (
            ApproveSelectedDistributionsResultSerializer(
                result
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary=(
                "Массово отменить распределения"
        ),
        description=(
                "Отменяет доступные распределения "
                "нагрузки из переданного списка ID. "
                "Причина отмены обязательна. Ошибка "
                "обработки одного распределения не "
                "останавливает остальные операции."
        ),
        request=(
                CancelSelectedDistributionsSerializer
        ),
        responses={
            200: (
                    CancelSelectedDistributionsResultSerializer
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            409: CONFLICT_RESPONSE,
        },
        examples=[
            OpenApiExample(
                name="Массовая отмена",
                value={
                    "ids": [
                        21,
                        22,
                    ],
                    "reason": (
                            "Исправление распределения "
                            "учебной нагрузки."
                    ),
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Результат отмены",
                value={
                    "requested_count": 2,
                    "found_count": 2,
                    "cancelled_count": 2,
                    "cancelled_ids": [
                        21,
                        22,
                    ],
                    "unavailable_count": 0,
                    "unavailable_ids": [],
                    "errors_count": 0,
                    "errors": [],
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="cancel-selected",
    )
    def cancel_selected(self, request):
        input_serializer = (
            CancelSelectedDistributionsSerializer(
                data=request.data
            )
        )
        input_serializer.is_valid(
            raise_exception=True
        )

        requested_ids = input_serializer.validated_data[
            "ids"
        ]
        reason = input_serializer.validated_data[
            "reason"
        ]

        distributions = list(
            self.get_queryset()
            .filter(pk__in=requested_ids)
            .order_by("pk")
        )

        found_ids = {
            distribution.pk
            for distribution in distributions
        }

        unavailable_ids = [
            distribution_id
            for distribution_id in requested_ids
            if distribution_id not in found_ids
        ]

        service_result = (
            WorkloadDistributionService
            .cancel_distributions(
                distributions=distributions,
                user=request.user,
                reason=reason,
            )
        )

        result = {
            "requested_count": len(requested_ids),
            "found_count": len(distributions),
            "cancelled_count": service_result[
                "cancelled_count"
            ],
            "cancelled_ids": service_result[
                "cancelled_ids"
            ],
            "unavailable_count": len(
                unavailable_ids
            ),
            "unavailable_ids": unavailable_ids,
            "errors_count": service_result[
                "errors_count"
            ],
            "errors": service_result["errors"],
        }

        output_serializer = (
            CancelSelectedDistributionsResultSerializer(
                result
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary=(
                "Массово восстановить распределения"
        ),
        description=(
                "Восстанавливает доступные отменённые "
                "распределения и переводит их в статус "
                "черновика. Причина восстановления "
                "обязательна."
        ),
        request=(
                RestoreSelectedDistributionsSerializer
        ),
        responses={
            200: (
                    RestoreSelectedDistributionsResultSerializer
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            409: CONFLICT_RESPONSE,
        },
        examples=[
            OpenApiExample(
                name="Массовое восстановление",
                value={
                    "ids": [
                        31,
                        32,
                    ],
                    "reason": (
                            "Распределения отменены "
                            "по ошибке."
                    ),
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Результат восстановления",
                value={
                    "requested_count": 2,
                    "found_count": 2,
                    "restored_count": 1,
                    "restored_ids": [
                        31,
                    ],
                    "unavailable_count": 0,
                    "unavailable_ids": [],
                    "errors_count": 1,
                    "errors": [
                        {
                            "id": 32,
                            "error": [
                                (
                                        "Распределение нельзя "
                                        "восстановить."
                                )
                            ],
                        }
                    ],
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="restore-selected",
    )
    def restore_selected(self, request):
        input_serializer = (
            RestoreSelectedDistributionsSerializer(
                data=request.data
            )
        )
        input_serializer.is_valid(
            raise_exception=True
        )

        requested_ids = input_serializer.validated_data[
            "ids"
        ]
        reason = input_serializer.validated_data[
            "reason"
        ]

        distributions = list(
            self.get_queryset()
            .filter(pk__in=requested_ids)
            .order_by("pk")
        )

        found_ids = {
            distribution.pk
            for distribution in distributions
        }

        unavailable_ids = [
            distribution_id
            for distribution_id in requested_ids
            if distribution_id not in found_ids
        ]

        service_result = (
            WorkloadDistributionService
            .restore_distributions(
                distributions=distributions,
                user=request.user,
                reason=reason,
            )
        )

        result = {
            "requested_count": len(requested_ids),
            "found_count": len(distributions),
            "restored_count": service_result[
                "restored_count"
            ],
            "restored_ids": service_result[
                "restored_ids"
            ],
            "unavailable_count": len(
                unavailable_ids
            ),
            "unavailable_ids": unavailable_ids,
            "errors_count": service_result[
                "errors_count"
            ],
            "errors": service_result["errors"],
        }

        output_serializer = (
            RestoreSelectedDistributionsResultSerializer(
                result
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary=(
                "Массово вернуть распределения "
                "в черновик"
        ),
        description=(
                "Возвращает доступные утверждённые или "
                "отменённые распределения в статус "
                "черновика. Причина возврата обязательна."
        ),
        request=(
                ReturnSelectedToDraftSerializer
        ),
        responses={
            200: (
                    ReturnSelectedToDraftResultSerializer
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            409: CONFLICT_RESPONSE,
        },
        examples=[
            OpenApiExample(
                name="Массовый возврат в черновик",
                value={
                    "ids": [
                        41,
                        42,
                    ],
                    "reason": (
                            "Необходимо скорректировать "
                            "распределённые часы."
                    ),
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Результат возврата",
                value={
                    "requested_count": 2,
                    "found_count": 2,
                    "returned_count": 2,
                    "returned_ids": [
                        41,
                        42,
                    ],
                    "unavailable_count": 0,
                    "unavailable_ids": [],
                    "errors_count": 0,
                    "errors": [],
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="return-selected-to-draft",
    )
    def return_selected_to_draft(self, request):
        input_serializer = (
            ReturnSelectedToDraftSerializer(
                data=request.data
            )
        )
        input_serializer.is_valid(
            raise_exception=True
        )

        requested_ids = input_serializer.validated_data[
            "ids"
        ]
        reason = input_serializer.validated_data[
            "reason"
        ]

        distributions = list(
            self.get_queryset()
            .filter(pk__in=requested_ids)
            .order_by("pk")
        )

        found_ids = {
            distribution.pk
            for distribution in distributions
        }

        unavailable_ids = [
            distribution_id
            for distribution_id in requested_ids
            if distribution_id not in found_ids
        ]

        service_result = (
            WorkloadDistributionService
            .return_distributions_to_draft(
                distributions=distributions,
                user=request.user,
                reason=reason,
            )
        )

        result = {
            "requested_count": len(requested_ids),
            "found_count": len(distributions),
            "returned_count": service_result[
                "returned_count"
            ],
            "returned_ids": service_result[
                "returned_ids"
            ],
            "unavailable_count": len(
                unavailable_ids
            ),
            "unavailable_ids": unavailable_ids,
            "errors_count": service_result[
                "errors_count"
            ],
            "errors": service_result["errors"],
        }

        output_serializer = (
            ReturnSelectedToDraftResultSerializer(
                result
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Сводки нагрузки"],
        summary=(
                "Получить сводку нагрузки "
                "преподавателей"
        ),
        description=(
                "Возвращает расчёт рекомендованной, "
                "распределённой и оставшейся нагрузки "
                "преподавателей за учебный год."
        ),
        parameters=[
            TeacherWorkloadSummaryQuerySerializer,
        ],
        request=None,
        responses={
            200: TeacherWorkloadSummarySerializer(
                many=True
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="teacher-summary",
    )
    def teacher_summary(
            self,
            request,
    ):
        query_serializer = (
            TeacherWorkloadSummaryQuerySerializer(
                data=request.query_params
            )
        )
        query_serializer.is_valid(
            raise_exception=True
        )

        academic_year = (
            self.get_academic_year_or_error(
                query_serializer.validated_data[
                    "academic_year"
                ]
            )
        )

        staff_member_id = (
            query_serializer.validated_data.get(
                "staff_member"
            )
        )
        department_id = (
            query_serializer.validated_data.get(
                "department"
            )
        )

        access_scope = (
            self.get_workload_access_scope()
        )

        self.validate_department_access(
            access_scope=access_scope,
            department_id=department_id,
        )

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

        output_serializer = (
            TeacherWorkloadSummarySerializer(
                result,
                many=True,
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Сводки нагрузки"],
        summary=(
                "Экспортировать сводку нагрузки "
                "преподавателей"
        ),
        description=(
                "Формирует Excel-файл со сводкой "
                "нагрузки преподавателей."
        ),
        parameters=[
            TeacherWorkloadSummaryQuerySerializer,
        ],
        request=None,
        responses={
            (
                    200,
                    EXCEL_CONTENT_TYPE,
            ): OpenApiTypes.BINARY,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="teacher-summary/export",
    )
    def export_teacher_summary(
            self,
            request,
    ):
        query_serializer = (
            TeacherWorkloadSummaryQuerySerializer(
                data=request.query_params
            )
        )
        query_serializer.is_valid(
            raise_exception=True
        )

        academic_year = (
            self.get_academic_year_or_error(
                query_serializer.validated_data[
                    "academic_year"
                ]
            )
        )

        staff_member_id = (
            query_serializer.validated_data.get(
                "staff_member"
            )
        )
        department_id = (
            query_serializer.validated_data.get(
                "department"
            )
        )

        access_scope = (
            self.get_workload_access_scope()
        )

        self.validate_department_access(
            access_scope=access_scope,
            department_id=department_id,
        )

        file_content, filename = (
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

        response = HttpResponse(
            content=file_content,
            content_type=EXCEL_CONTENT_TYPE,
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )
        response["Content-Length"] = str(
            len(file_content)
        )

        return response

    @extend_schema(
        tags=["Сводки нагрузки"],
        summary="Получить сводку нагрузки кафедр",
        description=(
                "Возвращает плановые, распределённые, "
                "утверждённые и оставшиеся часы кафедр "
                "за выбранный учебный год."
        ),
        parameters=[
            DepartmentWorkloadSummaryQuerySerializer,
        ],
        request=None,
        responses={
            200: DepartmentWorkloadSummarySerializer(
                many=True
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="department-summary",
    )
    def department_summary(
            self,
            request,
    ):
        query_serializer = (
            DepartmentWorkloadSummaryQuerySerializer(
                data=request.query_params
            )
        )
        query_serializer.is_valid(
            raise_exception=True
        )

        academic_year = (
            self.get_academic_year_or_error(
                query_serializer.validated_data[
                    "academic_year"
                ]
            )
        )

        academic_semester_id = (
            query_serializer.validated_data.get(
                "academic_semester"
            )
        )
        department_id = (
            query_serializer.validated_data.get(
                "department"
            )
        )

        access_scope = (
            self.get_workload_access_scope()
        )

        self.validate_department_access(
            access_scope=access_scope,
            department_id=department_id,
        )

        result = (
            DepartmentWorkloadService.get_summary(
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

        output_serializer = (
            DepartmentWorkloadSummarySerializer(
                result,
                many=True,
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Сводки нагрузки"],
        summary=(
                "Экспортировать сводку "
                "нагрузки кафедр"
        ),
        description=(
                "Формирует Excel-файл со сводкой "
                "нагрузки кафедр."
        ),
        parameters=[
            DepartmentWorkloadSummaryQuerySerializer,
        ],
        request=None,
        responses={
            (
                    200,
                    EXCEL_CONTENT_TYPE,
            ): OpenApiTypes.BINARY,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="department-summary/export",
    )
    def export_department_summary(
            self,
            request,
    ):
        query_serializer = (
            DepartmentWorkloadSummaryQuerySerializer(
                data=request.query_params
            )
        )
        query_serializer.is_valid(
            raise_exception=True
        )

        academic_year = (
            self.get_academic_year_or_error(
                query_serializer.validated_data[
                    "academic_year"
                ]
            )
        )

        academic_semester_id = (
            query_serializer.validated_data.get(
                "academic_semester"
            )
        )
        department_id = (
            query_serializer.validated_data.get(
                "department"
            )
        )

        access_scope = (
            self.get_workload_access_scope()
        )

        self.validate_department_access(
            access_scope=access_scope,
            department_id=department_id,
        )

        file_content, filename = (
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

        response = HttpResponse(
            content=file_content,
            content_type=EXCEL_CONTENT_TYPE,
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )
        response["Content-Length"] = str(
            len(file_content)
        )

        return response

    @staticmethod
    def get_academic_year_or_error(
            academic_year_id,
    ):
        """
        Возвращает активный учебный год либо
        формирует стандартную ошибку валидации.
        """

        try:
            return AcademicYear.objects.get(
                pk=academic_year_id,
                is_archived=False,
            )
        except AcademicYear.DoesNotExist as exc:
            raise ValidationError(
                {
                    "academic_year": (
                        "Указанный учебный год "
                        "не найден."
                    )
                }
            ) from exc

    def get_permissions(self):
        if self.action in (
                "create",
                "update",
                "partial_update",
                "destroy",
                "approve",
                "return_to_draft",
                "cancel",
                "restore",
                "transfer",
                "available_actions",
                "approve_selected",
                "return_selected_to_draft",
                "cancel_selected",
                "restore_selected",
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

    @extend_schema(
        tags=["Dashboard нагрузки"],
        summary="Получить dashboard нагрузки",
        description=(
                "Возвращает агрегированные показатели "
                "плановой и распределённой нагрузки, "
                "а также статистику по преподавателям "
                "и кафедрам."
        ),
        parameters=[
            WorkloadDashboardQuerySerializer,
        ],
        request=None,
        responses={
            200: WorkloadDashboardSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="dashboard",
    )
    def dashboard(
            self,
            request,
    ):
        query_serializer = (
            WorkloadDashboardQuerySerializer(
                data=request.query_params
            )
        )
        query_serializer.is_valid(
            raise_exception=True
        )

        academic_year = (
            self.get_academic_year_or_error(
                query_serializer.validated_data[
                    "academic_year"
                ]
            )
        )

        department_id = (
            query_serializer.validated_data.get(
                "department"
            )
        )

        access_scope = (
            self.get_workload_access_scope()
        )

        self.validate_department_access(
            access_scope=access_scope,
            department_id=department_id,
        )

        result = (
            WorkloadDashboardService.get_dashboard(
                academic_year=academic_year,
                department_id=department_id,
                allowed_department_ids=(
                    access_scope.department_ids
                ),
                allowed_staff_member_ids=(
                    access_scope.staff_member_ids
                ),
            )
        )

        output_serializer = (
            WorkloadDashboardSerializer(result)
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Dashboard нагрузки"],
        summary="Экспортировать dashboard нагрузки",
        description=(
                "Формирует Excel-файл с агрегированными "
                "показателями dashboard учебной нагрузки."
        ),
        parameters=[
            WorkloadDashboardQuerySerializer,
        ],
        request=None,
        responses={
            (
                    200,
                    EXCEL_CONTENT_TYPE,
            ): OpenApiTypes.BINARY,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="dashboard/export",
    )
    def export_dashboard(
            self,
            request,
    ):
        query_serializer = (
            WorkloadDashboardQuerySerializer(
                data=request.query_params
            )
        )
        query_serializer.is_valid(
            raise_exception=True
        )

        academic_year = (
            self.get_academic_year_or_error(
                query_serializer.validated_data[
                    "academic_year"
                ]
            )
        )

        department_id = (
            query_serializer.validated_data.get(
                "department"
            )
        )

        access_scope = (
            self.get_workload_access_scope()
        )

        self.validate_department_access(
            access_scope=access_scope,
            department_id=department_id,
        )

        file_content, filename = (
            WorkloadDashboardExportService.export(
                academic_year=academic_year,
                department_id=department_id,
                allowed_department_ids=(
                    access_scope.department_ids
                ),
                allowed_staff_member_ids=(
                    access_scope.staff_member_ids
                ),
            )
        )

        response = HttpResponse(
            content=file_content,
            content_type=EXCEL_CONTENT_TYPE,
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )
        response["Content-Length"] = str(
            len(file_content)
        )

        return response


class AcademicYearWorkloadValidationAPIView(
    APIView
):
    permission_classes = (
        IsAuthenticated,
        CanValidateAcademicYearWorkload,
    )

    @extend_schema(
        tags=["Учебная нагрузка"],
        summary="Проверить нагрузку учебного года",
        description=(
                "Выполняет комплексную проверку "
                "распределения учебной нагрузки "
                "за выбранный учебный год."
        ),
        parameters=[
            OpenApiParameter(
                name="academic_year",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID учебного года.",
            ),
        ],
        request=None,
        responses={
            200: (
                    AcademicYearWorkloadValidationResponseSerializer
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
    )
    def get(self, request):
        query_serializer = (
            AcademicYearValidationQuerySerializer(
                data=request.query_params
            )
        )
        query_serializer.is_valid(
            raise_exception=True
        )

        academic_year_id = (
            query_serializer.validated_data[
                "academic_year"
            ]
        )
        requested_department_id = (
            query_serializer.validated_data.get(
                "department"
            )
        )

        try:
            academic_year = AcademicYear.objects.get(
                pk=academic_year_id,
                is_archived=False,
            )
        except AcademicYear.DoesNotExist:
            raise ValidationError(
                {
                    "academic_year": (
                        "Указанный учебный год "
                        "не найден."
                    )
                }
            )

        department_ids = (
            WorkloadAccessService
            .resolve_validation_department_ids(
                user=request.user,
                requested_department_id=(
                    requested_department_id
                ),
            )
        )

        result = (
            AcademicYearWorkloadValidationService
            .validate(
                academic_year=academic_year,
                department_ids=department_ids,
                severity=(
                    query_serializer.validated_data.get(
                        "severity"
                    )
                ),
                issue_type=(
                    query_serializer.validated_data.get(
                        "issue_type"
                    )
                ),
            )
        )

        output_serializer = (
            AcademicYearValidationResultSerializer(
                result
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

class AcademicYearWorkloadValidationExportAPIView(
    APIView
):
    permission_classes = (
        IsAuthenticated,
        CanValidateAcademicYearWorkload,
    )

    @extend_schema(
        tags=["Учебная нагрузка"],
        summary=(
                "Экспортировать проверку нагрузки "
                "учебного года"
        ),
        description=(
                "Формирует Excel-файл с результатами "
                "проверки нагрузки учебного года."
        ),
        parameters=[
            OpenApiParameter(
                name="academic_year",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID учебного года.",
            ),
        ],
        request=None,
        responses={
            (
                    200,
                    (
                            "application/vnd.openxmlformats-"
                            "officedocument.spreadsheetml.sheet"
                    ),
            ): OpenApiTypes.BINARY,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
    )
    def get(self, request):
        query_serializer = (
            AcademicYearValidationQuerySerializer(
                data=request.query_params
            )
        )
        query_serializer.is_valid(
            raise_exception=True
        )

        academic_year_id = (
            query_serializer.validated_data[
                "academic_year"
            ]
        )
        requested_department_id = (
            query_serializer.validated_data.get(
                "department"
            )
        )

        try:
            academic_year = AcademicYear.objects.get(
                pk=academic_year_id,
                is_archived=False,
            )
        except AcademicYear.DoesNotExist as exc:
            raise ValidationError(
                {
                    "academic_year": (
                        "Указанный учебный год "
                        "не найден."
                    )
                }
            ) from exc

        department_ids = (
            WorkloadAccessService
            .resolve_validation_department_ids(
                user=request.user,
                requested_department_id=(
                    requested_department_id
                ),
            )
        )

        validation_result = (
            AcademicYearWorkloadValidationService
            .validate(
                academic_year=academic_year,
                department_ids=department_ids,
                severity=(
                    query_serializer.validated_data.get(
                        "severity"
                    )
                ),
                issue_type=(
                    query_serializer.validated_data.get(
                        "issue_type"
                    )
                ),
            )
        )

        excel_file = (
            AcademicYearValidationExcelService.build(
                validation_result=validation_result,
                generated_by=request.user,
            )
        )

        filename = (
            AcademicYearValidationExcelService
            .build_filename(
                validation_result=validation_result
            )
        )

        response = FileResponse(
            excel_file,
            content_type=(
                AcademicYearValidationExcelService
                .MIME_TYPE
            ),
            as_attachment=True,
            filename=filename,
        )

        response[
            "X-Validation-Errors-Count"
        ] = str(
            validation_result["summary"][
                "errors_count"
            ]
        )
        response[
            "X-Validation-Warnings-Count"
        ] = str(
            validation_result["summary"][
                "warnings_count"
            ]
        )
        response[
            "X-Validation-Is-Valid"
        ] = (
            "true"
            if validation_result["is_valid"]
            else "false"
        )

        return response

class AcademicYearClosingReadinessAPIView(
    APIView
):
    permission_classes = (
        IsAuthenticated,
        CanCheckAcademicYearClosingReadiness,
    )

    @extend_schema(
        tags=["Учебная нагрузка"],
        summary=(
                "Проверить готовность учебного года "
                "к закрытию"
        ),
        description=(
                "Проверяет наличие блокирующих проблем "
                "перед закрытием учебного года."
        ),
        parameters=[
            OpenApiParameter(
                name="academic_year",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID учебного года.",
            ),
        ],
        request=None,
        responses={
            200: (
                    AcademicYearClosingReadinessResponseSerializer
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
    )
    def get(self, request):
        query_serializer = (
            AcademicYearClosingReadinessQuerySerializer(
                data=request.query_params
            )
        )
        query_serializer.is_valid(
            raise_exception=True
        )

        academic_year_id = (
            query_serializer.validated_data[
                "academic_year"
            ]
        )
        requested_department_id = (
            query_serializer.validated_data.get(
                "department"
            )
        )

        try:
            academic_year = AcademicYear.objects.get(
                pk=academic_year_id,
                is_archived=False,
            )
        except AcademicYear.DoesNotExist as exc:
            raise ValidationError(
                {
                    "academic_year": (
                        "Указанный учебный год "
                        "не найден."
                    )
                }
            ) from exc

        department_ids = (
            WorkloadAccessService
            .resolve_validation_department_ids(
                user=request.user,
                requested_department_id=(
                    requested_department_id
                ),
            )
        )

        result = (
            AcademicYearClosingReadinessService
            .check(
                academic_year=academic_year,
                department_ids=department_ids,
            )
        )

        output_serializer = (
            AcademicYearClosingReadinessResultSerializer(
                result
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )