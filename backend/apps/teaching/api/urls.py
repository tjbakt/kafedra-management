from rest_framework.routers import DefaultRouter

from apps.teaching.api.views import (
    GroupCurriculumAssignmentViewSet,
    GroupSemesterViewSet,
    PlannedWorkloadViewSet,
    TeachingStreamGroupViewSet,
    TeachingStreamViewSet,
)


router = DefaultRouter()

router.register(
    "group-curricula",
    GroupCurriculumAssignmentViewSet,
    basename="group-curriculum",
)
router.register(
    "group-semesters",
    GroupSemesterViewSet,
    basename="group-semester",
)
router.register(
    "streams",
    TeachingStreamViewSet,
    basename="teaching-stream",
)
router.register(
    "stream-groups",
    TeachingStreamGroupViewSet,
    basename="teaching-stream-group",
)
router.register(
    "planned-workloads",
    PlannedWorkloadViewSet,
    basename="planned-workload",
)

urlpatterns = router.urls