from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, FileResponse

from decimal import Decimal

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
    WorkloadDistributionCreateSerializer,
    WorkloadDistributionUpdateSerializer,
    WorkloadDistributionPartialUpdateSerializer,
    WorkloadDistributionArchiveRestoreResponseSerializer,
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
    AssignSelectedPlannedWorkloadsSerializer,
    AssignSelectedPlannedWorkloadsResultSerializer,
    TeacherLoadSummarySerializer,
)
from apps.workload.models import WorkloadDistribution
from apps.teaching.models import PlannedWorkload

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
from apps.workload.services.teacher_load_summary import (
    TeacherLoadSummaryService,
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
from apps.common.api.schema_serializers import (
    ArchiveResponseSerializer,
)
from django.shortcuts import get_object_or_404



EXCEL_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument."
    "spreadsheetml.sheet"
)

WORKLOAD_DISTRIBUTION_LIST_PARAMETERS = [
    OpenApiParameter(
        name="academic_year",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description="ID учебного года.",
    ),
    OpenApiParameter(
        name="academic_semester",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description=(
            "ID семестра учебного года."
        ),
    ),
    OpenApiParameter(
        name="teaching_department",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description=(
            "ID кафедры плановой нагрузки."
        ),
    ),
    OpenApiParameter(
        name="faculty",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description="ID факультета.",
    ),
    OpenApiParameter(
        name="planned_workload",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description=(
            "ID плановой учебной нагрузки."
        ),
    ),
    OpenApiParameter(
        name="teaching_stream",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description="ID учебного потока.",
    ),
    OpenApiParameter(
        name="discipline",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description="ID дисциплины.",
    ),
    OpenApiParameter(
        name="workload_type",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description="ID вида учебной нагрузки.",
    ),
    OpenApiParameter(
        name="staff_member",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description="ID преподавателя.",
    ),
    OpenApiParameter(
        name="staff_employment",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description=(
            "ID трудового назначения "
            "преподавателя."
        ),
    ),
    OpenApiParameter(
        name="position",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description="ID должности.",
    ),
    OpenApiParameter(
        name="status",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        enum=[
            value
            for value, _label
            in WorkloadDistribution.Status.choices
        ],
        description=(
            "Бизнес-статус распределения."
        ),
    ),
    OpenApiParameter(
        name="search",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description=(
            "Поиск по табельному номеру и ФИО "
            "преподавателя, коду и названию потока, "
            "а также названию дисциплины."
        ),
    ),
    OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description=(
            "Сортировка по одному или нескольким "
            "полям через запятую. Разрешены: "
            "allocated_hours, created_at, "
            "staff_employment__staff_member__last_name, "
            "planned_workload__academic_year__start_year. "
            "Префикс '-' задаёт сортировку по убыванию."
        ),
        examples=[
            OpenApiExample(
                name="По часам по убыванию",
                value="-allocated_hours",
            ),
            OpenApiExample(
                name="Составная сортировка",
                value=(
                    "-planned_workload__"
                    "academic_year__start_year,"
                    "staff_employment__"
                    "staff_member__last_name"
                ),
            ),
        ],
    ),
    OpenApiParameter(
        name="page",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description=(
            "Номер страницы. Минимальное значение — 1."
        ),
    ),
    OpenApiParameter(
        name="page_size",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description=(
            "Количество записей на странице. "
            "По умолчанию 20, максимум 100."
        ),
    ),
]

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

        "planned_workload__teaching_stream__curriculum__code",

        "planned_workload__curriculum_workload__"
        "curriculum_discipline__discipline__code",

        "planned_workload__curriculum_workload__"
        "curriculum_discipline__discipline__name_ru",

        "planned_workload__curriculum_workload__"
        "curriculum_discipline__discipline__name_uz",

        "planned_workload__group_semester__"
        "group_curriculum__student_group__code"
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

    def get_serializer_class(self):
        if self.action == "create":
            return WorkloadDistributionCreateSerializer

        if self.action == "update":
            return WorkloadDistributionUpdateSerializer

        if self.action == "partial_update":
            return (
                WorkloadDistributionPartialUpdateSerializer
            )

        return WorkloadDistributionSerializer

    def get_queryset(self):
        queryset = WorkloadDistribution.objects.select_related(
            "planned_workload",
            "planned_workload__academic_year",
            "planned_workload__academic_semester",
            "planned_workload__teaching_department",
            "planned_workload__teaching_stream",
            "planned_workload__curriculum_workload",
            "planned_workload__curriculum_workload__workload_type",
            "planned_workload__teaching_stream__curriculum",
            "planned_workload__curriculum_workload__curriculum_discipline",
            "planned_workload__group_semester",
            "planned_workload__group_semester__group_curriculum",
            "planned_workload__group_semester__group_curriculum__student_group",
            "planned_workload__curriculum_workload__"
            "curriculum_discipline__discipline",
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
                            "staff_employment",
                            serializer.instance.staff_employment,
                        )
                    ),
                    allocated_hours=(
                        serializer.validated_data.get(
                            "allocated_hours",
                            serializer.instance.allocated_hours,
                        )
                    ),
                    notes=(
                        serializer.validated_data.get(
                            "notes",
                            serializer.instance.notes,
                        )
                    ),
                    user=self.request.user,
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

        serializer.instance = distribution

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary="Получить список распределений",
        description=(
                "Возвращает доступные текущему пользователю "
                "распределения учебной нагрузки.\n\n"
                "Поддерживаются фильтрация, поиск по данным "
                "преподавателя, потока и дисциплины, составная "
                "сортировка и постраничный вывод.\n\n"
                "Область данных дополнительно ограничивается "
                "правами текущего пользователя."
        ),
        parameters=(
                WORKLOAD_DISTRIBUTION_LIST_PARAMETERS
        ),
        responses={
            200: WorkloadDistributionSerializer(
                many=True
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
        },
    )
    def list(
            self,
            request,
            *args,
            **kwargs,
    ):
        return super().list(
            request,
            *args,
            **kwargs,
        )

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary="Получить распределение",
        description=(
                "Возвращает распределение учебной нагрузки "
                "по ID с кадровыми, учебными и аудиторскими "
                "полями."
        ),
        responses={
            200: WorkloadDistributionSerializer,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
    )
    def retrieve(
            self,
            request,
            *args,
            **kwargs,
    ):
        return super().retrieve(
            request,
            *args,
            **kwargs,
        )

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary="Создать распределение",
        description=(
                "Распределяет часть плановой учебной "
                "нагрузки преподавателю. Новое распределение "
                "создаётся в статусе черновика."
        ),
        request=WorkloadDistributionCreateSerializer,
        responses={
            201: WorkloadDistributionSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            409: CONFLICT_RESPONSE,
        },
        examples=[
            OpenApiExample(
                name="Создание распределения",
                value={
                    "planned_workload": 15,
                    "staff_employment": 8,
                    "allocated_hours": "36.00",
                    "notes": (
                            "Распределение лекционных часов."
                    ),
                },
                request_only=True,
            ),
        ],
    )
    def create(
            self,
            request,
            *args,
            **kwargs,
    ):
        input_serializer = self.get_serializer(
            data=request.data
        )
        input_serializer.is_valid(
            raise_exception=True
        )

        self.perform_create(
            input_serializer
        )

        output_serializer = (
            WorkloadDistributionSerializer(
                input_serializer.instance,
                context=self.get_serializer_context(),
            )
        )

        headers = self.get_success_headers(
            output_serializer.data
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary="Полностью изменить распределение",
        description=(
                "Изменяет преподавателя, количество часов "
                "и примечание чернового распределения. "
                "Плановая нагрузка после создания "
                "не изменяется."
        ),
        request=WorkloadDistributionUpdateSerializer,
        responses={
            200: WorkloadDistributionSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
            409: CONFLICT_RESPONSE,
        },
        examples=[
            OpenApiExample(
                name="Полное обновление",
                value={
                    "staff_employment": 9,
                    "allocated_hours": "42.00",
                    "notes": (
                            "Скорректировано распределение часов."
                    ),
                },
                request_only=True,
            ),
        ],
    )
    def update(
            self,
            request,
            *args,
            **kwargs,
    ):
        partial = kwargs.pop(
            "partial",
            False,
        )

        instance = self.get_object()

        input_serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        input_serializer.is_valid(
            raise_exception=True
        )

        self.perform_update(
            input_serializer
        )

        if getattr(
                instance,
                "_prefetched_objects_cache",
                None,
        ):
            instance._prefetched_objects_cache = {}

        output_serializer = (
            WorkloadDistributionSerializer(
                input_serializer.instance,
                context=self.get_serializer_context(),
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary="Частично изменить распределение",
        description=(
                "Частично изменяет преподавателя, "
                "количество часов или примечание "
                "чернового распределения."
        ),
        request=(
                WorkloadDistributionPartialUpdateSerializer
        ),
        responses={
            200: WorkloadDistributionSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
            409: CONFLICT_RESPONSE,
        },
        examples=[
            OpenApiExample(
                name="Изменение количества часов",
                value={
                    "allocated_hours": "24.00",
                },
                request_only=True,
            ),
        ],
    )
    def partial_update(
            self,
            request,
            *args,
            **kwargs,
    ):
        kwargs["partial"] = True

        return self.update(
            request,
            *args,
            **kwargs,
        )

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary="Архивировать распределение",
        description=(
                "Выполняет мягкое удаление распределения. "
                "Запись сохраняется в базе данных и "
                "перемещается в архив."
        ),
        request=None,
        responses={
            200: ArchiveResponseSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
            409: CONFLICT_RESPONSE,
        },
    )
    def destroy(
            self,
            request,
            *args,
            **kwargs,
    ):
        return super().destroy(
            request,
            *args,
            **kwargs,
        )

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary="Получить архивные распределения",
        description=(
                "Возвращает мягко удалённые распределения "
                "учебной нагрузки.\n\n"
                "Поддерживаются те же фильтры, поиск, "
                "сортировка и пагинация, что и для основного "
                "списка распределений."
        ),
        parameters=(
                WORKLOAD_DISTRIBUTION_LIST_PARAMETERS
        ),
        responses={
            200: WorkloadDistributionSerializer(
                many=True
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="archived",
    )
    def archived(
            self,
            request,
    ):
        return super().archived(request)

    @extend_schema(
        tags=["Распределение нагрузки"],
        summary=(
                "Восстановить распределение из архива"
        ),
        description=(
                "Восстанавливает мягко удалённое "
                "распределение из архива. Этот endpoint "
                "не меняет бизнес-статус распределения."
        ),
        request=None,
        responses={
            200: (
                    WorkloadDistributionArchiveRestoreResponseSerializer
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
        url_path="restore-archived",
    )
    def restore_archived(
            self,
            request,
            pk=None,
    ):
        queryset = (
            self.get_archived_queryset()
            .select_related(
                "planned_workload",
                "planned_workload__academic_year",
                "planned_workload__academic_semester",
                "planned_workload__teaching_department",
                "planned_workload__teaching_stream",
                "planned_workload__teaching_stream__curriculum",
                (
                    "planned_workload__curriculum_workload__"
                    "curriculum_discipline"
                ),
                (
                    "planned_workload__curriculum_workload__"
                    "curriculum_discipline__discipline"
                ),
                "planned_workload__curriculum_workload",
                (
                    "planned_workload__curriculum_workload__"
                    "workload_type"
                ),
                "staff_employment",
                "staff_employment__staff_member",
                "staff_employment__position",
                "staff_employment__department",
                "approved_by",
            )
        )

        distribution = get_object_or_404(
            queryset,
            pk=pk,
        )

        self.check_object_permissions(
            request,
            distribution,
        )

        try:
            WorkloadDistributionService.ensure_academic_year_open(
                academic_year=(
                    distribution
                    .planned_workload
                    .academic_year
                )
            )

            distribution.restore(
                user=request.user
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
            WorkloadDistributionSerializer(
                distribution,
                context=self.get_serializer_context(),
            )
        )

        return Response(
            {
                "detail": (
                    "Распределение восстановлено "
                    "из архива."
                ),
                "data": output_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

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

    @extend_schema(
        tags=[
            "Распределение нагрузки",
        ],
        summary=(
            "Массово назначить плановую "
            "нагрузку преподавателю"
        ),
        description=(
            "Создаёт отдельное черновое "
            "распределение для каждой выбранной "
            "позиции плановой нагрузки. "
            "Преподавателю назначается весь "
            "доступный остаток часов каждой позиции. "
            "Все позиции должны относиться к одному "
            "учебному году и одной кафедре."
        ),
        request=(
            AssignSelectedPlannedWorkloadsSerializer
        ),
        responses={
            200: (
                AssignSelectedPlannedWorkloadsResultSerializer
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
        },
    )
    @action(
        detail=False,
        methods=[
            "post",
        ],
        url_path="assign-selected",
    )
    def assign_selected(
        self,
        request,
    ):
        input_serializer = (
            AssignSelectedPlannedWorkloadsSerializer(
                data=request.data,
            )
        )

        input_serializer.is_valid(
            raise_exception=True,
        )

        requested_ids = (
            input_serializer
            .validated_data[
                "planned_workloads"
            ]
        )

        staff_employment = (
            input_serializer
            .validated_data[
                "staff_employment"
            ]
        )

        notes = (
            input_serializer
            .validated_data
            .get(
                "notes",
                "",
            )
        )

        access_scope = (
            self.get_workload_access_scope()
        )

        workloads = list(
            PlannedWorkload.objects
            .filter(
                pk__in=requested_ids,
                is_archived=False,
            )
            .select_related(
                "academic_year",
                "teaching_department",
                "curriculum_workload",
                (
                    "curriculum_workload__"
                    "workload_type"
                ),
                (
                    "curriculum_workload__"
                    "curriculum_discipline"
                ),
                (
                    "curriculum_workload__"
                    "curriculum_discipline__"
                    "discipline"
                ),
                "teaching_stream",
                "group_semester",
            )
            .order_by(
                "pk",
            )
        )

        workload_by_id = {
            workload.pk: workload
            for workload in workloads
        }

        accessible_workloads = []

        unavailable_ids = []

        for workload_id in requested_ids:
            workload = workload_by_id.get(
                workload_id
            )

            if workload is None:
                unavailable_ids.append(
                    workload_id
                )

                continue

            if not (
                access_scope
                .can_access_department(
                    workload
                    .teaching_department_id
                )
            ):
                unavailable_ids.append(
                    workload_id
                )

                continue

            accessible_workloads.append(
                workload
            )

        if accessible_workloads:
            academic_year_ids = {
                workload.academic_year_id
                for workload
                in accessible_workloads
            }

            department_ids = {
                workload
                .teaching_department_id
                for workload
                in accessible_workloads
            }

            if len(
                academic_year_ids
            ) != 1:
                raise ValidationError(
                    {
                        "planned_workloads": (
                            "Для массового назначения "
                            "выберите позиции одного "
                            "учебного года."
                        )
                    }
                )

            if len(
                department_ids
            ) != 1:
                raise ValidationError(
                    {
                        "planned_workloads": (
                            "Для массового назначения "
                            "выберите позиции одной "
                            "обеспечивающей кафедры."
                        )
                    }
                )

            department_id = next(
                iter(
                    department_ids
                )
            )

            if (
                staff_employment
                .department_id
                != department_id
            ):
                raise ValidationError(
                    {
                        "staff_employment": (
                            "Трудовое назначение "
                            "преподавателя должно "
                            "относиться к кафедре "
                            "выбранной плановой нагрузки."
                        )
                    }
                )

        created_ids = []

        errors = []

        allocated_hours_total = (
            Decimal("0.00")
        )

        for workload in accessible_workloads:
            try:
                remaining_hours = (
                    WorkloadDistributionService
                    .get_remaining_hours(
                        workload
                    )
                )

                if (
                    remaining_hours
                    <= Decimal("0.00")
                ):
                    raise DjangoValidationError(
                        {
                            "allocated_hours": (
                                "По позиции отсутствует "
                                "нераспределённый остаток "
                                "часов."
                            )
                        }
                    )

                distribution = (
                    WorkloadDistributionService
                    .create_distribution(
                        planned_workload=(
                            workload
                        ),
                        staff_employment=(
                            staff_employment
                        ),
                        allocated_hours=(
                            remaining_hours
                        ),
                        notes=notes,
                        user=request.user,
                    )
                )

                created_ids.append(
                    distribution.pk
                )

                allocated_hours_total += (
                    distribution
                    .allocated_hours
                )

            except DjangoValidationError as exc:
                errors.append(
                    {
                        "planned_workload": (
                            workload.pk
                        ),
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
                accessible_workloads
            ),

            "created_count": len(
                created_ids
            ),

            "created_ids": (
                created_ids
            ),

            "unavailable_count": len(
                unavailable_ids
            ),

            "unavailable_ids": (
                unavailable_ids
            ),

            "errors_count": len(
                errors
            ),

            "errors": errors,

            "allocated_hours": (
                allocated_hours_total
            ),
        }

        output_serializer = (
            AssignSelectedPlannedWorkloadsResultSerializer(
                result
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
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
                "cancel",
                "restore",
                "restore_archived",
                "return_to_draft",
                "transfer",
                "available_actions",
                "assign_selected",
                "approve_selected",
                "cancel_selected",
                "restore_selected",
                "return_selected_to_draft",
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

    @extend_schema(
        tags=[
            "Распределение нагрузки",
        ],
        summary=(
                "Итоговая нагрузка преподавателей"
        ),
        responses={
            200: TeacherLoadSummarySerializer(
                many=True,
            ),
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
        academic_year_id = request.query_params.get(
            "academic_year"
        )

        department_id = request.query_params.get(
            "department"
        )

        if not academic_year_id:
            raise ValidationError(
                {
                    "academic_year": (
                        "Необходимо указать "
                        "учебный год."
                    )
                }
            )

        if not department_id:
            raise ValidationError(
                {
                    "department": (
                        "Необходимо указать "
                        "кафедру."
                    )
                }
            )

        access_scope = (
            self.get_workload_access_scope()
        )

        if not access_scope.can_access_department(
                int(department_id)
        ):
            raise PermissionDenied()

        data = (
            TeacherLoadSummaryService
            .build_for_department(
                department_id=int(
                    department_id
                ),
                academic_year_id=int(
                    academic_year_id
                ),
            )
        )

        serializer = (
            TeacherLoadSummarySerializer(
                data,
                many=True,
            )
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


def get_active_academic_year_or_error(
    academic_year_id,
):
    """
    Возвращает неархивный учебный год либо
    стандартную ошибку валидации.
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

class AcademicYearWorkloadValidationAPIView(
    APIView
):
    permission_classes = (
        IsAuthenticated,
        CanValidateAcademicYearWorkload,
    )

    @extend_schema(
        tags=["Проверка учебного года"],
        summary= "Проверить нагрузку учебного года",
        description=(
            "Выполняет комплексную проверку "
            "учебной нагрузки выбранного года. "
            "Можно ограничить проверку кафедрой, "
            "уровнем серьёзности и типом проблемы."
        ),
        parameters=[
            AcademicYearValidationQuerySerializer,
        ],
        request=None,
        responses={
            200: AcademicYearValidationResultSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
        examples=[
            OpenApiExample(
                name="Результат проверки",
                value={
                    "academic_year": 3,
                    "academic_year_name": (
                        "2026/2027"
                    ),
                    "department_ids": [
                        2,
                        5,
                    ],
                    "is_valid": False,
                    "summary": {
                        "planned_workloads_count": 120,
                        "distributions_count": 116,
                        "year_staff_records_count": 34,
                        "issues_count": 2,
                        "errors_count": 1,
                        "warnings_count": 1,
                        "issues_by_type": {
                            "unallocated_workload": 1,
                            "staff_overload": 1,
                        },
                    },
                    "issues": [
                        {
                            "severity": "error",
                            "issue_type": (
                                "unallocated_workload"
                            ),
                            "message": (
                                "Нагрузка распределена "
                                "не полностью."
                            ),
                            "department_id": 2,
                            "department_name": (
                                "Кафедра информатики"
                            ),
                            "staff_employment_id": None,
                            "staff_member_id": None,
                            "teacher_name": None,
                            "planned_workload_id": 41,
                            "distribution_id": None,
                            "stream_code": "CS-101",
                            "discipline_name": (
                                "Программирование"
                            ),
                            "workload_type_name": (
                                "Лекционные занятия"
                            ),
                            "details": {
                                "planned_hours": "36.00",
                                "allocated_hours": "24.00",
                                "remaining_hours": "12.00",
                            },
                        }
                    ],
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(
        self,
        request,
    ):
        query_serializer = (
            AcademicYearValidationQuerySerializer(
                data=request.query_params
            )
        )
        query_serializer.is_valid(
            raise_exception=True
        )

        academic_year = (
            get_active_academic_year_or_error(
                query_serializer.validated_data[
                    "academic_year"
                ]
            )
        )

        requested_department_id = (
            query_serializer.validated_data.get(
                "department"
            )
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
        tags=["Проверка учебного года"],
        summary=(
            "Экспортировать результат проверки "
            "учебного года"
        ),
        description=(
            "Формирует Excel-файл с результатами "
            "проверки учебной нагрузки. Поддерживает "
            "те же фильтры, что и JSON endpoint."
        ),
        parameters=[
            AcademicYearValidationQuerySerializer,
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
    def get(
        self,
        request,
    ):
        query_serializer = (
            AcademicYearValidationQuerySerializer(
                data=request.query_params
            )
        )
        query_serializer.is_valid(
            raise_exception=True
        )

        academic_year = (
            get_active_academic_year_or_error(
                query_serializer.validated_data[
                    "academic_year"
                ]
            )
        )

        requested_department_id = (
            query_serializer.validated_data.get(
                "department"
            )
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
            content_type=EXCEL_CONTENT_TYPE,
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
        tags=["Проверка учебного года"],
        summary=(
            "Проверить готовность учебного года "
            "к закрытию"
        ),
        description=(
            "Проверяет наличие блокирующих проблем "
            "и предупреждений перед закрытием "
            "учебного года."
        ),
        parameters=[
            AcademicYearClosingReadinessQuerySerializer,
        ],
        request=None,
        responses={
            200: (
                AcademicYearClosingReadinessResultSerializer
            ),
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            403: FORBIDDEN_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
        examples=[
            OpenApiExample(
                name="Год не готов к закрытию",
                value={
                    "academic_year": 3,
                    "academic_year_name": (
                        "2026/2027"
                    ),
                    "department_ids": [
                        2,
                    ],
                    "ready_to_close": False,
                    "status": "not_ready",
                    "message": (
                        "Учебный год нельзя закрыть: "
                        "обнаружены блокирующие проблемы."
                    ),
                    "summary": {
                        "planned_workloads_count": 80,
                        "distributions_count": 78,
                        "year_staff_records_count": 22,
                        "blocking_issues_count": 1,
                        "warnings_count": 1,
                        "blocking_issues_by_type": {
                            "unallocated_workload": 1,
                        },
                        "warnings_by_type": {
                            "staff_overload": 1,
                        },
                    },
                    "blocking_issues": [
                        {
                            "severity": "error",
                            "issue_type": (
                                "unallocated_workload"
                            ),
                            "message": (
                                "Не вся нагрузка "
                                "распределена."
                            ),
                            "department_id": 2,
                            "department_name": (
                                "Кафедра информатики"
                            ),
                            "staff_employment_id": None,
                            "staff_member_id": None,
                            "teacher_name": None,
                            "planned_workload_id": 41,
                            "distribution_id": None,
                            "stream_code": "CS-101",
                            "discipline_name": (
                                "Программирование"
                            ),
                            "workload_type_name": (
                                "Лекционные занятия"
                            ),
                            "details": {},
                        }
                    ],
                    "warnings": [],
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(
        self,
        request,
    ):
        query_serializer = (
            AcademicYearClosingReadinessQuerySerializer(
                data=request.query_params
            )
        )
        query_serializer.is_valid(
            raise_exception=True
        )

        academic_year = (
            get_active_academic_year_or_error(
                query_serializer.validated_data[
                    "academic_year"
                ]
            )
        )

        requested_department_id = (
            query_serializer.validated_data.get(
                "department"
            )
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