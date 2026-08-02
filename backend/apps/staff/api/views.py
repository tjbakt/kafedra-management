from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.common.api.viewsets import BaseArchiveModelViewSet
from apps.common.api.mixins import (
    DjangoValidationErrorMixin,
)
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
    AcademicYearStaffRecordsResultSerializer,
    CreateAcademicYearStaffRecordsSerializer,
    RecommendedWorkloadQuerySerializer,
    RecommendedWorkloadSerializer,
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
from apps.staff.services.academic_year_staff_service import (
    AcademicYearStaffService,
)

from apps.access_control.models import SystemRole
from apps.access_control.services.access_service import (
    AccessService,
)


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
    def recommended_workload(
            self,
            request,
            pk=None,
    ):
        employment = self.get_object()

        query_serializer = (
            RecommendedWorkloadQuerySerializer(
                data=request.query_params
            )
        )
        query_serializer.is_valid(
            raise_exception=True
        )

        academic_year = (
            query_serializer.validated_data[
                "academic_year"
            ]
        )

        academic_year_record = (
            employment.get_academic_year_record(
                academic_year
            )
        )

        if academic_year_record is None:
            response_data = {
                "employment": employment.id,
                "academic_year": academic_year.id,
                "academic_year_name": (
                    academic_year.name
                ),
                "rate": None,
                "academic_degree": None,
                "academic_title": None,
                "has_academic_degree": None,
                "has_academic_title": None,
                "annual_hours": None,
                "norm_found": False,
                "academic_year_record_found": False,
                "message": (
                    "Для назначения не заполнены "
                    "кадровые данные на выбранный "
                    "учебный год."
                ),
            }
        else:
            norm = (
                academic_year_record
                .get_workload_norm()
            )

            response_data = {
                "employment": employment.id,
                "academic_year": academic_year.id,
                "academic_year_name": (
                    academic_year.name
                ),
                "academic_year_record": (
                    academic_year_record.id
                ),
                "academic_year_record_found": True,
                "rate": academic_year_record.rate,
                "academic_degree": (
                    academic_year_record
                    .academic_degree_id
                ),
                "academic_degree_name": (
                    str(
                        academic_year_record
                        .academic_degree
                    )
                    if (
                        academic_year_record
                        .academic_degree_id
                    )
                    else None
                ),
                "academic_title": (
                    academic_year_record
                    .academic_title_id
                ),
                "academic_title_name": (
                    str(
                        academic_year_record
                        .academic_title
                    )
                    if (
                        academic_year_record
                        .academic_title_id
                    )
                    else None
                ),
                "has_academic_degree": (
                    academic_year_record
                    .has_academic_degree
                ),
                "has_academic_title": (
                    academic_year_record
                    .has_academic_title
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
                    "Подходящая норма нагрузки "
                    "не установлена."
                )

        output_serializer = (
            RecommendedWorkloadSerializer(
                response_data
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

class StaffEmploymentAcademicYearViewSet(
    DjangoValidationErrorMixin,
    BaseArchiveModelViewSet,
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

    @staticmethod
    def base_queryset():
        """
        Общая структура запроса для активных
        и архивных записей.
        """

        return (
            StaffEmploymentAcademicYear.all_objects
            .select_related(
                "academic_year",
                "academic_degree",
                "academic_title",
                "staff_employment",
                "staff_employment__staff_member",
                "staff_employment__department",
                "staff_employment__department__faculty",
                (
                    "staff_employment__department__"
                    "faculty__university"
                ),
                "staff_employment__position",
            )
        )

    def get_queryset(self):
        queryset = self.base_queryset().filter(
            is_archived=False
        )

        return self.scope_queryset(queryset)

    def get_archived_queryset(self):
        queryset = self.base_queryset().filter(
            is_archived=True
        )

        return self.scope_queryset(queryset)

    def scope_queryset(self, queryset):
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

        filters = Q()

        if department_ids:
            filters |= Q(
                staff_employment__department_id__in=(
                    department_ids
                )
            )

        if own_staff_ids:
            filters |= Q(
                staff_employment__staff_member_id__in=(
                    own_staff_ids
                )
            )

        if not filters:
            return queryset.none()

        return queryset.filter(filters).distinct()

    def can_manage_department(
        self,
        *,
        user,
        department_id,
    ) -> bool:
        return (
            user.is_superuser
            or AccessService.has_global_role(
                user,
                SystemRole.Code.SYSTEM_ADMIN,
                SystemRole.Code.HR_OFFICER,
            )
            or AccessService.can_manage_department(
                user,
                department_id,
            )
        )

    def perform_create(self, serializer):
        employment = serializer.validated_data[
            "staff_employment"
        ]

        if not self.can_manage_department(
            user=self.request.user,
            department_id=employment.department_id,
        ):
            raise PermissionDenied(
                (
                    "Нет прав на создание кадровых "
                    "данных этой кафедры."
                )
            )

        super().perform_create(serializer)

    def perform_update(self, serializer):
        instance = self.get_object()

        new_employment = serializer.validated_data.get(
            "staff_employment",
            instance.staff_employment,
        )

        # Проверяем и исходную, и новую кафедру.
        department_ids = {
            instance.staff_employment.department_id,
            new_employment.department_id,
        }

        if not all(
            self.can_manage_department(
                user=self.request.user,
                department_id=department_id,
            )
            for department_id in department_ids
        ):
            raise PermissionDenied(
                (
                    "Нет прав на изменение кадровых "
                    "данных этой кафедры."
                )
            )

        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if not self.can_manage_department(
            user=self.request.user,
            department_id=(
                instance.staff_employment.department_id
            ),
        ):
            raise PermissionDenied(
                (
                    "Нет прав на архивирование кадровых "
                    "данных этой кафедры."
                )
            )

        super().perform_destroy(instance)

    def check_restore_permission(
        self,
        request,
        instance,
    ):
        if not self.can_manage_department(
            user=request.user,
            department_id=(
                instance
                .staff_employment
                .department_id
            ),
        ):
            raise PermissionDenied(
                (
                    "Нет прав на восстановление кадровых "
                    "данных этой кафедры."
                )
            )

    def check_bulk_create_permission(
            self,
            *,
            user,
            department,
    ):
        if user.is_superuser:
            return

        if AccessService.has_global_role(
                user,
                SystemRole.Code.SYSTEM_ADMIN,
                SystemRole.Code.HR_OFFICER,
        ):
            return

        if department is None:
            raise PermissionDenied(
                (
                    "Массовое заполнение всех кафедр "
                    "доступно только кадровой службе "
                    "или системному администратору."
                )
            )

        if not AccessService.can_manage_department(
                user,
                department.id,
        ):
            raise PermissionDenied(
                (
                    "Нет прав на массовое заполнение "
                    "данных выбранной кафедры."
                )
            )

    @action(
        detail=False,
        methods=["post"],
        url_path="create-missing",
    )
    def create_missing(self, request):
        input_serializer = (
            CreateAcademicYearStaffRecordsSerializer(
                data=request.data,
                context=self.get_serializer_context(),
            )
        )
        input_serializer.is_valid(
            raise_exception=True
        )

        academic_year = (
            input_serializer.validated_data[
                "academic_year"
            ]
        )
        department = (
            input_serializer.validated_data.get(
                "department"
            )
        )

        self.check_bulk_create_permission(
            user=request.user,
            department=department,
        )

        result = (
            AcademicYearStaffService
            .create_missing_records(
                academic_year=academic_year,
                department=department,
                created_by=request.user,
            )
        )

        missing_count = (
            AcademicYearStaffService
            .get_missing_employments(
                academic_year=academic_year,
                department=department,
            )
            .count()
        )

        response_data = {
            "academic_year": academic_year.id,
            "academic_year_name": str(
                academic_year
            ),
            "department": (
                department.id
                if department is not None
                else None
            ),
            "department_name": (
                str(department)
                if department is not None
                else None
            ),
            "total_employments": result[
                "total_employments"
            ],
            "created": result["created"],
            "restored": result["restored"],
            "skipped": result["skipped"],
            "missing": missing_count,
        }

        output_serializer = (
            AcademicYearStaffRecordsResultSerializer(
                response_data
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="missing",
    )
    def missing(self, request):
        input_serializer = (
            MissingAcademicYearStaffRecordsSerializer(
                data=request.query_params,
                context=self.get_serializer_context(),
            )
        )
        input_serializer.is_valid(
            raise_exception=True
        )

        academic_year = (
            input_serializer.validated_data[
                "academic_year"
            ]
        )
        department = (
            input_serializer.validated_data.get(
                "department"
            )
        )

        self.check_missing_list_permission(
            user=request.user,
            department=department,
        )

        queryset = (
            AcademicYearStaffService
            .get_missing_employments(
                academic_year=academic_year,
                department=department,
            )
        )

        page = self.paginate_queryset(queryset)

        if page is not None:
            data = [
                self.serialize_missing_employment(
                    employment
                )
                for employment in page
            ]
            return self.get_paginated_response(data)

        return Response(
            [
                self.serialize_missing_employment(
                    employment
                )
                for employment in queryset
            ]
        )

    @staticmethod
    def serialize_missing_employment(
            employment,
    ):
        staff_member = employment.staff_member

        return {
            "staff_employment": employment.id,
            "staff_member": staff_member.id,
            "staff_member_name": (
                staff_member.full_name
            ),
            "personnel_number": (
                staff_member.personnel_number
            ),
            "department": employment.department_id,
            "department_name": str(
                employment.department
            ),
            "position": employment.position_id,
            "position_name": str(
                employment.position
            ),
            "current_rate": employment.rate,
            "current_academic_degree": (
                staff_member.academic_degree_id
            ),
            "current_academic_degree_name": (
                str(staff_member.academic_degree)
                if staff_member.academic_degree_id
                else None
            ),
            "current_academic_title": (
                staff_member.academic_title_id
            ),
            "current_academic_title_name": (
                str(staff_member.academic_title)
                if staff_member.academic_title_id
                else None
            ),
        }

    def check_missing_list_permission(
            self,
            *,
            user,
            department,
    ):
        if user.is_superuser:
            return

        if AccessService.has_global_role(
                user,
                SystemRole.Code.SYSTEM_ADMIN,
                SystemRole.Code.HR_OFFICER,
                SystemRole.Code.ACADEMIC_OFFICE,
        ):
            return

        if department is None:
            raise PermissionDenied(
                (
                    "Для просмотра всех кафедр "
                    "недостаточно прав."
                )
            )

        department_ids = (
            AccessService.accessible_department_ids(
                user,
                role_codes=(
                    SystemRole.Code.DEPARTMENT_HEAD,
                ),
            )
        )

        if (
                not department_ids
                or department.id not in department_ids
        ):
            raise PermissionDenied(
                (
                    "Нет прав на просмотр данных "
                    "выбранной кафедры."
                )
            )

class WorkloadNormViewSet(
    DjangoValidationErrorMixin,
    BaseArchiveModelViewSet,
):
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