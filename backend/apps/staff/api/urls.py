from rest_framework.routers import DefaultRouter

from apps.staff.api.views import (
    AcademicDegreeViewSet,
    AcademicTitleViewSet,
    StaffEmploymentAcademicYearViewSet,
    StaffEmploymentViewSet,
    StaffMemberViewSet,
    StaffPositionViewSet,
    WorkloadNormViewSet,
)


router = DefaultRouter()

router.register(
    "positions",
    StaffPositionViewSet,
    basename="staff-position",
)
router.register(
    "academic-degrees",
    AcademicDegreeViewSet,
    basename="academic-degree",
)
router.register(
    "academic-titles",
    AcademicTitleViewSet,
    basename="academic-title",
)
router.register(
    "members",
    StaffMemberViewSet,
    basename="staff-member",
)
router.register(
    "employments",
    StaffEmploymentViewSet,
    basename="staff-employment",
)
router.register(
    "employment-academic-years",
    StaffEmploymentAcademicYearViewSet,
    basename="staff-employment-academic-year",
)
router.register(
    "workload-norms",
    WorkloadNormViewSet,
    basename="workload-norm",
)

urlpatterns = router.urls