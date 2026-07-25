from rest_framework.routers import DefaultRouter

from apps.access_control.api.views import (
    SystemRoleViewSet,
    UserRoleAssignmentViewSet,
)


router = DefaultRouter()

router.register(
    "roles",
    SystemRoleViewSet,
    basename="system-role",
)
router.register(
    "assignments",
    UserRoleAssignmentViewSet,
    basename="user-role-assignment",
)

urlpatterns = router.urls