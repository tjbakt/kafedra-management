from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.academics.api.filters import (
    AcademicSemesterFilter,
    AcademicYearFilter,
    EducationDurationFilter,
    StudentGroupFilter,
    StudyProgramFilter,
)
from apps.academics.api.serializers import (
    AcademicSemesterSerializer,
    AcademicYearSerializer,
    EducationDurationSerializer,
    EducationLevelSerializer,
    StudentGroupSerializer,
    StudyFormSerializer,
    StudyProgramSerializer,
    AcademicYearClosingOperationResultSerializer,
    CloseAcademicYearSerializer,
    ReopenAcademicYearSerializer,
)
from apps.academics.models import (
    AcademicSemester,
    AcademicYear,
    EducationDuration,
    EducationLevel,
    StudentGroup,
    StudyForm,
    StudyProgram,
)
from apps.academics.exceptions import (
    AcademicYearClosingError,
)
from apps.common.api.mixins import (
    DjangoValidationErrorMixin,
)
from apps.common.api.viewsets import BaseArchiveModelViewSet
from apps.access_control.permissions import (
    CanCloseAcademicYear,
)
from apps.academics.services.academic_year_closing_service import (
    AcademicYearClosingService,
)


def academic_year_closing_result(
    academic_year,
):
    def user_name(user):
        if user is None:
            return None

        full_name = user.get_full_name().strip()

        return full_name or str(user)

    return {
        "id": academic_year.pk,
        "name": academic_year.name,
        "status": academic_year.status,
        "status_label": (
            academic_year.get_status_display()
        ),
        "is_current": academic_year.is_current,
        "is_active": academic_year.is_active,

        "closed_at": academic_year.closed_at,
        "closed_by": academic_year.closed_by_id,
        "closed_by_name": user_name(
            academic_year.closed_by
        ),
        "closing_comment": (
            academic_year.closing_comment
        ),

        "reopened_at": academic_year.reopened_at,
        "reopened_by": academic_year.reopened_by_id,
        "reopened_by_name": user_name(
            academic_year.reopened_by
        ),
        "reopening_reason": (
            academic_year.reopening_reason
        ),
    }

class AcademicYearViewSet(BaseArchiveModelViewSet):
    model = AcademicYear
    queryset = (
        AcademicYear.objects
        .select_related(
            "closed_by",
            "reopened_by",
            "created_by",
            "updated_by",
            "archived_by",
        )
        .all()
    )
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AcademicYearFilter
    ordering_fields = (
        "start_year",
        "end_year",
        "status",
        "closed_at",
        "created_at",
    )
    ordering = ("-start_year",)

    def get_permissions(self):
        if self.action in (
                "close",
                "reopen",
        ):
            permission_classes = (
                IsAuthenticated,
                CanCloseAcademicYear,
            )
        else:
            permission_classes = (
                IsAuthenticated,
            )

        return [
            permission()
            for permission in permission_classes
        ]

    @action(
        detail=True,
        methods=["post"],
        url_path="close",
    )
    def close(
            self,
            request,
            pk=None,
    ):
        academic_year = self.get_object()

        input_serializer = (
            CloseAcademicYearSerializer(
                data=request.data
            )
        )
        input_serializer.is_valid(
            raise_exception=True
        )

        try:
            closed_year, readiness = (
                AcademicYearClosingService.close(
                    academic_year=academic_year,
                    user=request.user,
                    comment=(
                        input_serializer
                        .validated_data
                        .get("comment", "")
                    ),
                )
            )
        except AcademicYearClosingError as exc:
            response_data = {
                "code": exc.code,
                "message": exc.message,
            }

            response_data.update(
                exc.details
            )

            return Response(
                response_data,
                status=(
                    status.HTTP_409_CONFLICT
                ),
            )

        closed_year.refresh_from_db()

        result = academic_year_closing_result(
            closed_year
        )
        result["readiness"] = readiness

        output_serializer = (
            AcademicYearClosingOperationResultSerializer(
                result
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="reopen",
    )
    def reopen(
            self,
            request,
            pk=None,
    ):
        academic_year = self.get_object()

        input_serializer = (
            ReopenAcademicYearSerializer(
                data=request.data
            )
        )
        input_serializer.is_valid(
            raise_exception=True
        )

        try:
            reopened_year = (
                AcademicYearClosingService.reopen(
                    academic_year=academic_year,
                    user=request.user,
                    reason=(
                        input_serializer
                        .validated_data["reason"]
                    ),
                )
            )
        except AcademicYearClosingError as exc:
            return Response(
                {
                    "code": exc.code,
                    "message": exc.message,
                    **exc.details,
                },
                status=(
                    status.HTTP_409_CONFLICT
                ),
            )

        reopened_year.refresh_from_db()

        result = academic_year_closing_result(
            reopened_year
        )

        output_serializer = (
            AcademicYearClosingOperationResultSerializer(
                result
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class EducationLevelViewSet(BaseArchiveModelViewSet):
    model = EducationLevel
    queryset = EducationLevel.objects.all()
    serializer_class = EducationLevelSerializer
    permission_classes = [IsAuthenticated]
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
    )
    ordering_fields = (
        "sort_order",
        "name_ru",
        "code",
    )
    ordering = (
        "sort_order",
        "name_ru",
    )


class StudyFormViewSet(BaseArchiveModelViewSet):
    model = StudyForm
    queryset = StudyForm.objects.all()
    serializer_class = StudyFormSerializer
    permission_classes = [IsAuthenticated]
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
    )
    ordering_fields = (
        "sort_order",
        "name_ru",
        "code",
    )
    ordering = (
        "sort_order",
        "name_ru",
    )


class EducationDurationViewSet(BaseArchiveModelViewSet):
    model = EducationDuration
    serializer_class = EducationDurationSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = EducationDurationFilter
    ordering_fields = (
        "duration_months",
        "semesters_count",
        "created_at",
    )

    def get_queryset(self):
        return EducationDuration.objects.select_related(
            "education_level",
            "study_form",
        )


class AcademicSemesterViewSet(DjangoValidationErrorMixin, BaseArchiveModelViewSet,):
    model = AcademicSemester
    serializer_class = AcademicSemesterSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AcademicSemesterFilter
    ordering_fields = (
        "start_date",
        "end_date",
        "created_at",
    )
    ordering = ("-start_date",)

    def get_queryset(self):
        return AcademicSemester.objects.select_related(
            "academic_year",
        )


class StudyProgramViewSet(BaseArchiveModelViewSet):
    model = StudyProgram
    serializer_class = StudyProgramSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StudyProgramFilter
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
        "profiling_department__name_ru",
        "profiling_department__name_uz",
    )
    ordering_fields = (
        "code",
        "name_ru",
        "sort_order",
        "created_at",
    )
    ordering = (
        "sort_order",
        "code",
    )

    def get_queryset(self):
        return StudyProgram.objects.select_related(
            "university",
            "education_level",
            "profiling_department",
            "profiling_department__faculty",
        )


class StudentGroupViewSet(BaseArchiveModelViewSet):
    model = StudentGroup
    serializer_class = StudentGroupSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StudentGroupFilter
    search_fields = (
        "code",
        "study_program__name_ru",
        "study_program__name_uz",
        "faculty__name_ru",
        "faculty__name_uz",
    )
    ordering_fields = (
        "code",
        "student_count",
        "created_at",
        "academic_year_admission__start_year",
    )
    ordering = (
        "-academic_year_admission__start_year",
        "code",
    )

    def get_queryset(self):
        return StudentGroup.objects.select_related(
            "academic_year_admission",
            "graduation_academic_year",
            "faculty",
            "faculty__university",
            "study_form",
            "study_program",
            "study_program__education_level",
            "study_program__profiling_department",
            "study_program__profiling_department__faculty",
        )