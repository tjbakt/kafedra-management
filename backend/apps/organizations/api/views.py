from django.db import models
from django.db.models import Count
from rest_framework.permissions import IsAuthenticated

from apps.common.api.viewsets import (
    BaseArchiveModelViewSet,
)
from apps.organizations.api.filters import (
    DepartmentFilter,
    FacultyFilter,
    UniversityFilter,
)
from apps.organizations.api.serializers import (
    DepartmentSerializer,
    FacultySerializer,
    UniversitySerializer,
)
from apps.organizations.models import (
    Department,
    Faculty,
    University,
)


class UniversityViewSet(BaseArchiveModelViewSet):
    model = University
    serializer_class = UniversitySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = UniversityFilter
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
        "name_uz",
        "sort_order",
        "created_at",
    )
    ordering = (
        "sort_order",
        "name_ru",
    )

    def get_queryset(self):
        return (
            University.objects
            .annotate(
                faculties_count=Count(
                    "faculties",
                    filter=(
                        models.Q(
                            faculties__is_archived=False
                        )
                    ),
                )
            )
        )

    def get_archived_queryset(self):
        return (
            University.all_objects
            .archived()
            .annotate(
                faculties_count=Count(
                    "faculties",
                    filter=models.Q(
                        faculties__is_archived=False
                    ),
                )
            )
        )


class FacultyViewSet(BaseArchiveModelViewSet):
    model = Faculty
    serializer_class = FacultySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = FacultyFilter
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
        "short_name_ru",
        "short_name_uz",
        "university__name_ru",
        "university__name_uz",
    )
    ordering_fields = (
        "code",
        "name_ru",
        "name_uz",
        "faculty_type",
        "sort_order",
        "created_at",
    )
    ordering = (
        "sort_order",
        "name_ru",
    )

    def get_queryset(self):
        return (
            Faculty.objects
            .select_related("university")
            .annotate(
                departments_count=Count(
                    "departments",
                    filter=(
                        models.Q(
                            departments__is_archived=False
                        )
                    ),
                )
            )
        )

    def get_archived_queryset(self):
        return (
            Faculty.all_objects
            .archived()
            .select_related("university")
            .annotate(
                departments_count=Count(
                    "departments",
                    filter=models.Q(
                        departments__is_archived=False
                    ),
                )
            )
        )


class DepartmentViewSet(BaseArchiveModelViewSet):
    model = Department
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = DepartmentFilter
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
        "short_name_ru",
        "short_name_uz",
        "faculty__name_ru",
        "faculty__name_uz",
    )
    ordering_fields = (
        "code",
        "name_ru",
        "name_uz",
        "sort_order",
        "created_at",
    )
    ordering = (
        "sort_order",
        "name_ru",
    )

    def get_queryset(self):
        return Department.objects.select_related(
            "faculty",
            "faculty__university",
        )

    def get_archived_queryset(self):
        return (
            Department.all_objects
            .archived()
            .select_related(
                "faculty",
                "faculty__university",
            )
        )