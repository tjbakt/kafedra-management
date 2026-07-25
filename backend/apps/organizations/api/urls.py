from rest_framework.routers import DefaultRouter

from apps.organizations.api.views import (
    DepartmentViewSet,
    FacultyViewSet,
    UniversityViewSet,
)


router = DefaultRouter()

router.register(
    "universities",
    UniversityViewSet,
    basename="university",
)
router.register(
    "faculties",
    FacultyViewSet,
    basename="faculty",
)
router.register(
    "departments",
    DepartmentViewSet,
    basename="department",
)

urlpatterns = router.urls