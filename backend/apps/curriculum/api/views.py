from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.api.mixins import (
    DjangoValidationErrorMixin,
)
from apps.common.api.viewsets import BaseArchiveModelViewSet
from apps.curriculum.api.filters import (
    CurriculumDisciplineFilter,
    CurriculumFilter,
    CurriculumWorkloadFilter,
    DisciplineFilter,
    WorkloadTypeFilter,
)
from apps.curriculum.api.serializers import (
    AcademicYearCreditNormSerializer,
    AcademicYearWorkloadNormSerializer,
    CurriculumDisciplineSerializer,
    CurriculumSerializer,
    CurriculumWorkloadSerializer,
    CurriculumDisciplineBundleSerializer,
    CurriculumWorkloadRuleSerializer,
    DisciplineSerializer,
    WorkloadTypeSerializer,
)
from apps.curriculum.models import (
    AcademicYearCreditNorm,
    AcademicYearWorkloadNorm,
    Curriculum,
    CurriculumDiscipline,
    CurriculumWorkload,
    CurriculumWorkloadRule,
    Discipline,
    WorkloadType,
)

from apps.curriculum.services.norm_resolver import (
    resolve_curriculum_academic_year,
    resolve_curriculum_credit_norm,
)


class DisciplineViewSet(BaseArchiveModelViewSet):
    model = Discipline
    serializer_class = DisciplineSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = DisciplineFilter
    search_fields = ("code", "name_ru", "name_uz")
    ordering_fields = ("code", "name_ru", "sort_order")
    ordering = ("sort_order", "name_ru")

    def get_queryset(self):
        return (
            Discipline.objects.select_related(
                "default_department",
                "default_department__faculty",
            ).prefetch_related(
                "workload_types",
            )
        )

class WorkloadTypeViewSet(BaseArchiveModelViewSet):
    model = WorkloadType
    queryset = WorkloadType.objects.all()
    serializer_class = WorkloadTypeSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = WorkloadTypeFilter
    search_fields = ("code", "name_ru", "name_uz")
    ordering_fields = ("sort_order", "name_ru")
    ordering = ("sort_order", "name_ru")


class CurriculumViewSet(DjangoValidationErrorMixin, BaseArchiveModelViewSet,):
    model = Curriculum
    serializer_class = CurriculumSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = CurriculumFilter
    search_fields = (
        "code",
        "study_program__code",
        "study_program__name_ru",
        "study_program__name_uz",
    )
    ordering_fields = (
        "code",
        "version",
        "effective_academic_year__start_year",
        "created_at",
    )
    ordering = (
        "-effective_academic_year__start_year",
        "study_program__code",
        "-version",
    )

    def get_queryset(self):
        return (
            Curriculum.objects
            .select_related(
                "study_program",
                "study_program__education_level",
                "study_form",
                "effective_academic_year",
            )
            .annotate(
                disciplines_count=Count(
                    "curriculum_disciplines",
                    distinct=True,
                )
            )
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="planning-norms",
    )
    def planning_norms(
            self,
            request,
            pk=None,
    ):
        curriculum = self.get_object()

        academic_year = (
            resolve_curriculum_academic_year(
                curriculum
            )
        )

        credit_norm = (
            resolve_curriculum_credit_norm(
                curriculum
            )
        )

        annual_norms = (
            AcademicYearWorkloadNorm
            .objects
            .filter(
                academic_year=academic_year,
                is_active=True,
                is_archived=False,
            )
            .select_related(
                "workload_type"
            )
        )

        return Response(
            {
                "academic_year":
                    academic_year.id,

                "academic_year_name":
                    str(academic_year),

                "hours_per_credit":
                    (
                        str(
                            credit_norm
                            .hours_per_credit
                        )
                        if credit_norm
                        else None
                    ),

                "workload_norms": [
                    {
                        "workload_type":
                            item.workload_type_id,

                        "code":
                            item.workload_type.code,

                        "coefficient":
                            str(
                                item.coefficient
                            ),
                    }
                    for item in annual_norms
                ],
            }
        )


class CurriculumDisciplineViewSet(DjangoValidationErrorMixin, BaseArchiveModelViewSet,):
    model = CurriculumDiscipline
    serializer_class = CurriculumDisciplineSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = CurriculumDisciplineFilter
    search_fields = (
        "discipline__code",
        "discipline__name_ru",
        "discipline__name_uz",
        "teaching_department__name_ru",
    )
    ordering_fields = (
        "semester_number",
        "discipline__name_ru",
        "credits",
        "total_academic_hours",
    )
    ordering = (
        "curriculum",
        "semester_number",
        "discipline__name_ru",
    )

    @action(
        detail=False,
        methods=["post"],
        url_path="configure",
    )
    def configure(
        self,
        request,
    ):
        serializer = (
            CurriculumDisciplineBundleSerializer(
                data=request.data,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        records = serializer.save()

        response_serializer = (
            CurriculumDisciplineSerializer(
                records,
                many=True,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "detail": (
                    "Дисциплина и виды "
                    "нагрузки сохранены."
                ),
                "data":
                    response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def get_queryset(self):
        return (
            CurriculumDiscipline.objects
            .select_related(
                "curriculum",
                (
                    "curriculum__"
                    "effective_academic_year"
                ),
                "curriculum__study_program",
                "discipline",
                "teaching_department",
                "teaching_department__faculty",
            )
            .prefetch_related(
                "workload_items",
                "workload_items__workload_type",
            )
        )


class CurriculumWorkloadViewSet(DjangoValidationErrorMixin, BaseArchiveModelViewSet,):
    model = CurriculumWorkload
    serializer_class = CurriculumWorkloadSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = CurriculumWorkloadFilter
    search_fields = (
        "curriculum_discipline__discipline__code",
        "curriculum_discipline__discipline__name_ru",
        "workload_type__name_ru",
    )
    ordering_fields = (
        "base_hours",
        "workload_type__sort_order",
    )
    ordering = (
        "curriculum_discipline",
        "workload_type__sort_order",
    )

    def get_queryset(self):
        return CurriculumWorkload.objects.select_related(
            "curriculum_discipline",
            (
                "curriculum_discipline__"
                "discipline"
            ),
            (
                "curriculum_discipline__"
                "curriculum"
            ),
            (
                "curriculum_discipline__"
                "curriculum__"
                "effective_academic_year"
            ),
            "workload_type",
        )

class CurriculumWorkloadRuleViewSet(
    DjangoValidationErrorMixin,
    BaseArchiveModelViewSet,
):
    model = CurriculumWorkloadRule

    serializer_class = (
        CurriculumWorkloadRuleSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    filterset_fields = (
        "curriculum",
        "workload_type",
        "calculation_mode",
        "is_active",
    )

    ordering = (
        "workload_type__sort_order",
        "workload_type__name_ru",
    )

    def get_queryset(self):
        return (
            CurriculumWorkloadRule
            .objects
            .select_related(
                "curriculum",
                "workload_type",
            )
        )

class AcademicYearWorkloadNormViewSet(
    DjangoValidationErrorMixin,
    BaseArchiveModelViewSet,
):
    model = AcademicYearWorkloadNorm

    serializer_class = (
        AcademicYearWorkloadNormSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    filterset_fields = (
        "academic_year",
        "workload_type",
        "is_active",
    )

    ordering = (
        "-academic_year__start_year",
        "workload_type__sort_order",
    )

    def get_queryset(self):
        return (
            AcademicYearWorkloadNorm
            .objects
            .select_related(
                "academic_year",
                "workload_type",
            )
        )


class AcademicYearCreditNormViewSet(
    DjangoValidationErrorMixin,
    BaseArchiveModelViewSet,
):
    model = AcademicYearCreditNorm

    serializer_class = (
        AcademicYearCreditNormSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    filterset_fields = (
        "academic_year",
    )

    ordering = (
        "-academic_year__start_year",
    )

    def get_queryset(self):
        return (
            AcademicYearCreditNorm
            .objects
            .select_related(
                "academic_year",
            )
        )