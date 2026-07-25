from rest_framework.routers import DefaultRouter

from apps.notifications.api.views import (
    NotificationViewSet,
    UserTaskViewSet,
)


router = DefaultRouter()

router.register(
    "notifications",
    NotificationViewSet,
    basename="notification",
)
router.register(
    "tasks",
    UserTaskViewSet,
    basename="user-task",
)

urlpatterns = router.urls