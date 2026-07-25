from rest_framework.permissions import IsAuthenticated

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
from apps.common.api.viewsets import BaseArchiveModelViewSet


class AcademicYearViewSet(BaseArchiveModelViewSet):
    model = AcademicYear
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AcademicYearFilter
    ordering_fields = (
        "start_year",
        "end_year",
        "created_at",
    )
    ordering = ("-start_year",)


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


class AcademicSemesterViewSet(BaseArchiveModelViewSet):
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