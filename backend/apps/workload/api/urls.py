from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.workload.api.views import (
    WorkloadDistributionViewSet,
    AcademicYearWorkloadValidationAPIView,
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
]

urlpatterns += router.urls