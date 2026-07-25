from django.db import transaction
from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.api.viewsets import BaseArchiveModelViewSet
from apps.teaching.api.filters import (
    GroupCurriculumAssignmentFilter,
    GroupSemesterFilter,
    PlannedWorkloadFilter,
    TeachingStreamFilter,
    TeachingStreamGroupFilter,
)
from apps.teaching.api.serializers import (
    GroupCurriculumAssignmentSerializer,
    GroupSemesterSerializer,
    PlannedWorkloadSerializer,
    TeachingStreamGroupSerializer,
    TeachingStreamSerializer,
)
from apps.teaching.models import (
    GroupCurriculumAssignment,
    GroupSemester,
    PlannedWorkload,
    TeachingStream,
    TeachingStreamGroup,
)
from apps.teaching.services.workload_calculator import (
    TeachingStreamWorkloadCalculator,
)

class GroupCurriculumAssignmentViewSet(
    BaseArchiveModelViewSet
):
    model = GroupCurriculumAssignment
    serializer_class = GroupCurriculumAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = GroupCurriculumAssignmentFilter
    search_fields = (
        "student_group__code",
        "curriculum__code",
        "curriculum__study_program__name_ru",
    )
    ordering_fields = (
        "student_group__code",
        "start_academic_year__start_year",
        "created_at",
    )
    ordering = (
        "-start_academic_year__start_year",
        "student_group__code",
    )

    def get_queryset(self):
        return (
            GroupCurriculumAssignment.objects
            .select_related(
                "student_group",
                "student_group__study_program",
                "student_group__study_form",
                "curriculum",
                "curriculum__study_program",
                "curriculum__study_form",
                "start_academic_year",
                "end_academic_year",
            )
        )

class GroupSemesterViewSet(BaseArchiveModelViewSet):
    model = GroupSemester
    serializer_class = GroupSemesterSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = GroupSemesterFilter
    search_fields = (
        "group_curriculum__student_group__code",
        "group_curriculum__curriculum__code",
    )
    ordering_fields = (
        "semester_number",
        "students_count",
        "academic_year__start_year",
    )
    ordering = (
        "-academic_year__start_year",
        "semester_number",
        "group_curriculum__student_group__code",
    )

    def get_queryset(self):
        return GroupSemester.objects.select_related(
            "group_curriculum",
            "group_curriculum__student_group",
            "group_curriculum__student_group__faculty",
            "group_curriculum__student_group__study_program",
            "group_curriculum__curriculum",
            "academic_year",
            "academic_semester",
        )

class TeachingStreamGroupViewSet(
    BaseArchiveModelViewSet
):
    model = TeachingStreamGroup
    serializer_class = TeachingStreamGroupSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TeachingStreamGroupFilter
    search_fields = (
        "teaching_stream__code",
        "group_semester__group_curriculum__"
        "student_group__code",
    )
    ordering = (
        "teaching_stream__code",
        "group_semester__group_curriculum__"
        "student_group__code",
    )

    def get_queryset(self):
        return TeachingStreamGroup.objects.select_related(
            "teaching_stream",
            "group_semester",
            "group_semester__group_curriculum",
            "group_semester__group_curriculum__student_group",
        )

class TeachingStreamViewSet(BaseArchiveModelViewSet):
    model = TeachingStream
    serializer_class = TeachingStreamSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TeachingStreamFilter
    search_fields = (
        "code",
        "name",
        "curriculum_discipline__discipline__name_ru",
        "curriculum_discipline__discipline__name_uz",
        "teaching_department__name_ru",
    )
    ordering_fields = (
        "code",
        "name",
        "academic_year__start_year",
        "created_at",
    )
    ordering = (
        "-academic_year__start_year",
        "academic_semester__season",
        "code",
    )

    def get_queryset(self):
        return (
            TeachingStream.objects
            .select_related(
                "academic_year",
                "academic_semester",
                "curriculum_discipline",
                "curriculum_discipline__curriculum",
                "curriculum_discipline__discipline",
                "curriculum_workload",
                "curriculum_workload__workload_type",
                "teaching_department",
            )
            .prefetch_related(
                "stream_groups",
                "stream_groups__group_semester",
                "stream_groups__group_semester__"
                "group_curriculum",
                "stream_groups__group_semester__"
                "group_curriculum__student_group",
            )
            .distinct()
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="calculate",
    )
    def calculate(self, request, pk=None):
        stream = self.get_object()

        try:
            calculator = TeachingStreamWorkloadCalculator(
                stream
            )
            planned_workload = calculator.calculate(
                teaching_stream=stream,
                user=request.user
            )
        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PlannedWorkloadSerializer(
            planned_workload,
            context=self.get_serializer_context(),
        )

        return Response(
            {
                "detail": "Плановая нагрузка рассчитана.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="calculate-all",
    )
    def calculate_all(self, request):
        queryset = self.filter_queryset(
            self.get_queryset()
        )

        calculated = []
        errors = []

        with transaction.atomic():
            for stream in queryset:
                try:
                    workload = (
                        TeachingStreamWorkloadCalculator(
                            stream
                        ).calculate(user=request.user)
                    )
                    calculated.append(workload.id)
                except ValueError as exc:
                    errors.append(
                        {
                            "stream": stream.id,
                            "code": stream.code,
                            "error": str(exc),
                        }
                    )

        return Response(
            {
                "calculated_count": len(calculated),
                "calculated_ids": calculated,
                "errors_count": len(errors),
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )

class PlannedWorkloadViewSet(
    BaseArchiveModelViewSet
):
    model = PlannedWorkload
    serializer_class = PlannedWorkloadSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PlannedWorkloadFilter
    http_method_names = (
        "get",
        "patch",
        "delete",
        "head",
        "options",
    )
    search_fields = (
        "teaching_stream__code",
        "teaching_stream__name",
        "teaching_stream__curriculum_discipline__"
        "discipline__name_ru",
        "teaching_department__name_ru",
    )
    ordering_fields = (
        "total_hours",
        "calculated_at",
        "academic_year__start_year",
    )
    ordering = (
        "-academic_year__start_year",
        "teaching_department__name_ru",
        "teaching_stream__code",
    )

    def get_queryset(self):
        return PlannedWorkload.objects.select_related(
            "teaching_stream",
            "teaching_stream__curriculum_discipline",
            "teaching_stream__curriculum_discipline__discipline",
            "academic_year",
            "academic_semester",
            "teaching_department",
            "curriculum_workload",
            "curriculum_workload__workload_type",
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="summary",
    )
    def summary(self, request):
        queryset = self.filter_queryset(
            self.get_queryset()
        )

        total = queryset.aggregate(
            total_hours=Sum("total_hours")
        )["total_hours"] or 0

        by_department = (
            queryset
            .values(
                "teaching_department_id",
                "teaching_department__name_ru",
            )
            .annotate(
                total_hours=Sum("total_hours")
            )
            .order_by(
                "teaching_department__name_ru"
            )
        )

        by_workload_type = (
            queryset
            .values(
                "curriculum_workload__workload_type_id",
                "curriculum_workload__"
                "workload_type__name_ru",
            )
            .annotate(
                total_hours=Sum("total_hours")
            )
            .order_by(
                "curriculum_workload__"
                "workload_type__sort_order"
            )
        )

        return Response(
            {
                "total_hours": total,
                "by_department": list(by_department),
                "by_workload_type": list(
                    by_workload_type
                ),
            }
        )