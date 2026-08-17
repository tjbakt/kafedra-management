from rest_framework.routers import DefaultRouter

from apps.curriculum.api.views import (
    AcademicYearCreditNormViewSet,
    AcademicYearWorkloadNormViewSet,
    CurriculumDisciplineViewSet,
    CurriculumViewSet,
    CurriculumWorkloadViewSet,
    CurriculumWorkloadRuleViewSet,
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

router.register(
    "academic-year-workload-norms",
    AcademicYearWorkloadNormViewSet,
    basename="academic-year-workload-norm",
)

router.register(
    "academic-year-credit-norms",
    AcademicYearCreditNormViewSet,
    basename="academic-year-credit-norm",
)

router.register(
    "curriculum-workload-rules",
    CurriculumWorkloadRuleViewSet,
    basename="curriculum-workload-rule",
)

urlpatterns = router.urls