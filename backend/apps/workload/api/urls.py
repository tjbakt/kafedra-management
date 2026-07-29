from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.workload.api.views import (
    WorkloadDistributionViewSet,
    AcademicYearWorkloadValidationAPIView,
    AcademicYearWorkloadValidationExportAPIView,
)


router = DefaultRouter()

router.register(
    "distributions",
    WorkloadDistributionViewSet,
    basename="workload-distribution",
)

urlpatterns = [
    path(
        "validation/academic-year/",
        AcademicYearWorkloadValidationAPIView.as_view(),
        name="workload-academic-year-validation",
    ),
    path(
        "validation/academic-year/export/",
        AcademicYearWorkloadValidationExportAPIView.as_view(),
        name="workload-academic-year-validation-export",
    ),
]

urlpatterns += router.urls