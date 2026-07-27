from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.academics.models import AcademicYear
from apps.common.api.viewsets import BaseArchiveModelViewSet
from apps.staff.models import StaffEmployment, WorkloadNorm
from apps.teaching.models import PlannedWorkload
from apps.workload.api.filters import (
    WorkloadDistributionFilter,
)
from apps.workload.api.serializers import (
    WorkloadDistributionSerializer,
)
from apps.workload.models import WorkloadDistribution
from apps.workload.services.distribution_service import (
    WorkloadDistributionService,
)

from apps.access_control.models import SystemRole
from apps.access_control.services.access_service import (
    AccessService,
)

from apps.access_control.permissions import (
    CanManageWorkloadDistribution,
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

            if not academic_year_id:
                return Response(
                    {
                        "detail": (
                            "Необходимо указать academic_year."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            academic_year = AcademicYear.objects.get(
                pk=academic_year_id
            )

            employments = (
                StaffEmployment.objects
                .select_related(
                    "staff_member",
                    "position",
                    "department",
                )
                .filter(
                    is_active=True,
                    position__is_teaching_position=True,
                )
            )

            if staff_member_id:
                employments = employments.filter(
                    staff_member_id=staff_member_id
                )

            result = []

            for employment in employments:
                distributed_hours = (
                        WorkloadDistribution.objects
                        .filter(
                            staff_employment=employment,
                            planned_workload__academic_year=(
                                academic_year
                            ),
                            status__in=(
                                WorkloadDistribution.Status.DRAFT,
                                WorkloadDistribution.Status.APPROVED,
                            ),
                        )
                        .aggregate(
                            total=Sum("allocated_hours")
                        )["total"]
                        or Decimal("0.00")
                )

                norm = WorkloadNorm.objects.filter(
                    academic_year=academic_year,
                    rate=employment.rate,
                    has_academic_degree=(
                        employment.staff_member
                        .has_academic_degree
                    ),
                    has_academic_title=(
                        employment.staff_member
                        .has_academic_title
                    ),
                    is_active=True,
                ).first()

                recommended_hours = (
                    norm.annual_hours if norm else None
                )

                if recommended_hours:
                    difference_hours = (
                            distributed_hours
                            - recommended_hours
                    )
                    load_percent = (
                            distributed_hours
                            / recommended_hours
                            * Decimal("100.00")
                    ).quantize(Decimal("0.01"))
                else:
                    difference_hours = None
                    load_percent = None

                result.append(
                    {
                        "staff_employment": employment.id,
                        "staff_member": (
                            employment.staff_member_id
                        ),
                        "teacher_name": (
                            employment.staff_member.full_name
                        ),
                        "personnel_number": (
                            employment.staff_member
                            .personnel_number
                        ),
                        "department": employment.department_id,
                        "department_name": (
                            employment.department.name_ru
                        ),
                        "position": employment.position_id,
                        "position_name": (
                            employment.position.name_ru
                        ),
                        "academic_year": academic_year.id,
                        "academic_year_name": academic_year.name,
                        "employment_rate": employment.rate,
                        "recommended_hours": recommended_hours,
                        "distributed_hours": distributed_hours,
                        "difference_hours": difference_hours,
                        "load_percent": load_percent,
                        "norm_found": norm is not None,
                    }
                )

            return Response(result)

        @action(
            detail=False,
            methods=["get"],
            url_path="department-summary",
        )
        def department_summary(self, request):
            queryset = self.filter_queryset(
                self.get_queryset()
            )

            distributed_total = (
                    queryset.aggregate(
                        total=Sum("allocated_hours")
                    )["total"]
                    or Decimal("0.00")
            )

            planned_queryset = PlannedWorkload.objects.all()

            academic_year = request.query_params.get(
                "academic_year"
            )
            academic_semester = request.query_params.get(
                "academic_semester"
            )
            department = request.query_params.get(
                "teaching_department"
            )

            if academic_year:
                planned_queryset = planned_queryset.filter(
                    academic_year_id=academic_year
                )

            if academic_semester:
                planned_queryset = planned_queryset.filter(
                    academic_semester_id=academic_semester
                )

            if department:
                planned_queryset = planned_queryset.filter(
                    teaching_department_id=department
                )

            planned_total = (
                    planned_queryset.aggregate(
                        total=Sum("total_hours")
                    )["total"]
                    or Decimal("0.00")
            )

            remaining_total = (
                    planned_total - distributed_total
            )

            by_teacher = (
                queryset
                .values(
                    "staff_employment__staff_member_id",
                    "staff_employment__staff_member__"
                    "personnel_number",
                    "staff_employment__staff_member__last_name",
                    "staff_employment__staff_member__first_name",
                    "staff_employment__staff_member__middle_name",
                )
                .annotate(
                    distributed_hours=Sum("allocated_hours")
                )
                .order_by(
                    "staff_employment__staff_member__last_name",
                    "staff_employment__staff_member__first_name",
                )
            )

            return Response(
                {
                    "planned_hours": planned_total,
                    "distributed_hours": distributed_total,
                    "remaining_hours": remaining_total,
                    "distribution_percent": (
                        (
                                distributed_total
                                / planned_total
                                * Decimal("100.00")
                        ).quantize(Decimal("0.01"))
                        if planned_total
                        else Decimal("0.00")
                    ),
                    "by_teacher": list(by_teacher),
                }
            )

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