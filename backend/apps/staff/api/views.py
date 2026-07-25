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
    StaffEmploymentAcademicYearFilter,
    StaffEmploymentFilter,
    StaffMemberFilter,
    StaffPositionFilter,
    WorkloadNormFilter,
)
from apps.staff.api.serializers import (
    AcademicDegreeSerializer,
    AcademicTitleSerializer,
    StaffEmploymentAcademicYearSerializer,
    StaffEmploymentSerializer,
    StaffMemberSerializer,
    StaffPositionSerializer,
    WorkloadNormSerializer,
)
from apps.staff.models import (
    AcademicDegree,
    AcademicTitle,
    StaffEmployment,
    StaffEmploymentAcademicYear,
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

        academic_year = request.query_params.get(
            "academic_year"
        )

        academic_year_record = (
            employment.get_academic_year_record(
                academic_year
            )
        )

        if academic_year_record is None:
            return Response(
                {
                    "employment": employment.id,
                    "academic_year": academic_year.id,
                    "academic_year_name": academic_year.name,
                    "rate": None,
                    "academic_degree": None,
                    "academic_title": None,
                    "has_academic_degree": None,
                    "has_academic_title": None,
                    "annual_hours": None,
                    "norm_found": False,
                    "academic_year_record_found": False,
                    "message": (
                        "Для назначения не заполнены кадровые "
                        "данные на выбранный учебный год."
                    ),
                },
                status=status.HTTP_200_OK,
            )

        norm = academic_year_record.get_workload_norm()

        response_data = {
            "employment": employment.id,
            "academic_year": academic_year.id,
            "academic_year_name": academic_year.name,
            "academic_year_record": (
                academic_year_record.id
            ),
            "academic_year_record_found": True,
            "rate": academic_year_record.rate,
            "academic_degree": (
                academic_year_record.academic_degree_id
            ),
            "academic_degree_name": (
                str(academic_year_record.academic_degree)
                if academic_year_record.academic_degree_id
                else None
            ),
            "academic_title": (
                academic_year_record.academic_title_id
            ),
            "academic_title_name": (
                str(academic_year_record.academic_title)
                if academic_year_record.academic_title_id
                else None
            ),
            "has_academic_degree": (
                academic_year_record.has_academic_degree
            ),
            "has_academic_title": (
                academic_year_record.has_academic_title
            ),
            "annual_hours": (
                norm.annual_hours
                if norm is not None
                else None
            ),
            "norm_found": norm is not None,
        }

        if norm is not None:
            response_data["norm_id"] = norm.id
        else:
            response_data["message"] = (
                "Подходящая норма нагрузки не установлена."
            )

        return Response(
            response_data,
            status=status.HTTP_200_OK,
        )

class StaffEmploymentAcademicYearViewSet(
    BaseArchiveModelViewSet
):
    model = StaffEmploymentAcademicYear
    serializer_class = (
        StaffEmploymentAcademicYearSerializer
    )
    permission_classes = [IsAuthenticated]
    filterset_class = (
        StaffEmploymentAcademicYearFilter
    )
    search_fields = (
        "staff_employment__staff_member__personnel_number",
        "staff_employment__staff_member__last_name",
        "staff_employment__staff_member__first_name",
        "staff_employment__staff_member__middle_name",
        "staff_employment__department__name_ru",
        "staff_employment__department__name_uz",
        "staff_employment__position__name_ru",
        "academic_degree__name_ru",
        "academic_title__name_ru",
    )
    ordering_fields = (
        "academic_year__start_year",
        "rate",
        "staff_employment__staff_member__last_name",
        "created_at",
    )
    ordering = (
        "-academic_year__start_year",
        "staff_employment__staff_member__last_name",
        "staff_employment__staff_member__first_name",
    )

    def get_queryset(self):
        queryset = (
            StaffEmploymentAcademicYear.objects
            .select_related(
                "academic_year",
                "academic_degree",
                "academic_title",
                "staff_employment",
                "staff_employment__staff_member",
                "staff_employment__department",
                "staff_employment__department__faculty",
                (
                    "staff_employment__department__faculty__"
                    "university"
                ),
                "staff_employment__position",
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
            AccessService.accessible_staff_member_ids(
                user
            )
        )

        if (
            department_ids is None
            or own_staff_ids is None
        ):
            return queryset

        return queryset.filter(
            Q(
                staff_employment__department_id__in=(
                    department_ids
                )
            )
            | Q(
                staff_employment__staff_member_id__in=(
                    own_staff_ids
                )
            )
        ).distinct()

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