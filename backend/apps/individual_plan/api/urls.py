from rest_framework.routers import DefaultRouter

from apps.individual_plan.api.views import (
    IndividualActivityTypeViewSet,
    IndividualPlanItemViewSet,
    IndividualPlanSectionViewSet,
    IndividualPlanViewSet,
)


router = DefaultRouter()

router.register(
    "sections",
    IndividualPlanSectionViewSet,
    basename="individual-plan-section",
)
router.register(
    "activity-types",
    IndividualActivityTypeViewSet,
    basename="individual-activity-type",
)
router.register(
    "plans",
    IndividualPlanViewSet,
    basename="individual-plan",
)
router.register(
    "items",
    IndividualPlanItemViewSet,
    basename="individual-plan-item",
)

urlpatterns = router.urls