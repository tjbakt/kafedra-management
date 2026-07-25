from rest_framework.routers import DefaultRouter

from apps.curriculum.api.views import (
    CurriculumDisciplineViewSet,
    CurriculumViewSet,
    CurriculumWorkloadViewSet,
    DisciplineViewSet,
    WorkloadTypeViewSet,
)


router = DefaultRouter()

router.register(
    "disciplines",
    DisciplineViewSet,
    basename="discipline",
)
router.register(
    "workload-types",
    WorkloadTypeViewSet,
    basename="workload-type",
)
router.register(
    "curricula",
    CurriculumViewSet,
    basename="curriculum",
)
router.register(
    "curriculum-disciplines",
    CurriculumDisciplineViewSet,
    basename="curriculum-discipline",
)
router.register(
    "curriculum-workloads",
    CurriculumWorkloadViewSet,
    basename="curriculum-workload",
)

urlpatterns = router.urls