from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.academics.models import AcademicYear
from apps.common.api.viewsets import BaseArchiveModelViewSet
from apps.staff.api.filters import (
    AcademicDegreeFilter,
    AcademicTitleFilter,
    StaffEmploymentFilter,
    StaffMemberFilter,
    StaffPositionFilter,
    WorkloadNormFilter,
)
from apps.staff.api.serializers import (
    AcademicDegreeSerializer,
    AcademicTitleSerializer,
    StaffEmploymentSerializer,
    StaffMemberSerializer,
    StaffPositionSerializer,
    WorkloadNormSerializer,
)
from apps.staff.models import (
    AcademicDegree,
    AcademicTitle,
    StaffEmployment,
    StaffMember,
    StaffPosition,
    WorkloadNorm,
)

from apps.access_control.models import SystemRole
from apps.access_control.services.access_service import (
    AccessService,
)

from django.db.models import Q


class StaffPositionViewSet(BaseArchiveModelViewSet):
    model = StaffPosition
    queryset = StaffPosition.objects.all()
    serializer_class = StaffPositionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StaffPositionFilter
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
    )
    ordering_fields = (
        "code",
        "name_ru",
        "sort_order",
    )
    ordering = (
        "sort_order",
        "name_ru",
    )


class AcademicDegreeViewSet(BaseArchiveModelViewSet):
    model = AcademicDegree
    queryset = AcademicDegree.objects.all()
    serializer_class = AcademicDegreeSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AcademicDegreeFilter
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
        "short_name_ru",
        "short_name_uz",
    )
    ordering_fields = (
        "code",
        "name_ru",
        "sort_order",
    )
    ordering = (
        "sort_order",
        "name_ru",
    )


class AcademicTitleViewSet(BaseArchiveModelViewSet):
    model = AcademicTitle
    queryset = AcademicTitle.objects.all()
    serializer_class = AcademicTitleSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AcademicTitleFilter
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
        "short_name_ru",
        "short_name_uz",
    )
    ordering_fields = (
        "code",
        "name_ru",
        "sort_order",
    )
    ordering = (
        "sort_order",
        "name_ru",
    )

class StaffMemberViewSet(BaseArchiveModelViewSet):
    model = StaffMember
    serializer_class = StaffMemberSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StaffMemberFilter
    search_fields = (
        "personnel_number",
        "last_name",
        "first_name",
        "middle_name",
        "phone",
        "email",
    )
    ordering_fields = (
        "personnel_number",
        "last_name",
        "first_name",
        "created_at",
    )
    ordering = (
        "last_name",
        "first_name",
        "middle_name",
    )

    def get_queryset(self):
        queryset = (
            StaffMember.objects
            .select_related(
                "user",
                "academic_degree",
                "academic_title",
            )
            .prefetch_related(
                "employments",
                "employments__department",
                "employments__position",
            )
        )

        user = self.request.user

        if user.is_superuser:
            return queryset

        if AccessService.has_global_role(
            user,
            SystemRole.Code.SYSTEM_ADMIN,
            SystemRole.Code.HR_OFFICER,
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
                employments__department_id__in=department_ids
            )
            | Q(id__in=own_staff_ids)
        ).distinct()


class StaffEmploymentViewSet(BaseArchiveModelViewSet):
    model = StaffEmployment
    serializer_class = StaffEmploymentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StaffEmploymentFilter
    search_fields = (
        "staff_member__personnel_number",
        "staff_member__last_name",
        "staff_member__first_name",
        "staff_member__middle_name",
        "department__name_ru",
        "department__name_uz",
        "position__name_ru",
        "position__name_uz",
    )
    ordering_fields = (
        "start_date",
        "end_date",
        "rate",
        "staff_member__last_name",
    )
    ordering = (
        "staff_member__last_name",
        "-is_primary",
        "-start_date",
    )

    def get_queryset(self):
        return StaffEmployment.objects.select_related(
            "staff_member",
            "staff_member__academic_degree",
            "staff_member__academic_title",
            "department",
            "department__faculty",
            "position",
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="recommended-workload",
    )
    def recommended_workload(self, request, pk=None):
        employment = self.get_object()

        academic_year_id = request.query_params.get(
            "academic_year"
        )

        if not academic_year_id:
            return Response(
                {
                    "detail": (
                        "Необходимо указать параметр "
                        "academic_year."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        academic_year = get_object_or_404(
            AcademicYear.objects,
            pk=academic_year_id,
        )

        norm = employment.get_workload_norm(
            academic_year=academic_year
        )

        if norm is None:
            return Response(
                {
                    "employment": employment.id,
                    "academic_year": academic_year.id,
                    "academic_year_name": academic_year.name,
                    "rate": employment.rate,
                    "has_academic_degree": (
                        employment.staff_member
                        .has_academic_degree
                    ),
                    "has_academic_title": (
                        employment.staff_member
                        .has_academic_title
                    ),
                    "annual_hours": None,
                    "norm_found": False,
                    "message": (
                        "Подходящая норма нагрузки "
                        "не установлена."
                    ),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "employment": employment.id,
                "academic_year": academic_year.id,
                "academic_year_name": academic_year.name,
                "rate": employment.rate,
                "has_academic_degree": (
                    employment.staff_member
                    .has_academic_degree
                ),
                "has_academic_title": (
                    employment.staff_member
                    .has_academic_title
                ),
                "annual_hours": norm.annual_hours,
                "norm_found": True,
                "norm_id": norm.id,
            },
            status=status.HTTP_200_OK,
        )


class WorkloadNormViewSet(BaseArchiveModelViewSet):
    model = WorkloadNorm
    serializer_class = WorkloadNormSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = WorkloadNormFilter
    ordering_fields = (
        "rate",
        "annual_hours",
        "academic_year__start_year",
        "created_at",
    )
    ordering = (
        "-academic_year__start_year",
        "-rate",
    )

    def get_queryset(self):
        return WorkloadNorm.objects.select_related(
            "academic_year",
        )