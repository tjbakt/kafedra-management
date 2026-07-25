from rest_framework.routers import DefaultRouter

from apps.workload.api.views import (
    WorkloadDistributionViewSet,
)


router = DefaultRouter()

router.register(
    "distributions",
    WorkloadDistributionViewSet,
    basename="workload-distribution",
)

urlpatterns = router.urls