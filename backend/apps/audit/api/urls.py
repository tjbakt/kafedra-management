from rest_framework.routers import DefaultRouter

from apps.audit.api.views import AuditEventViewSet


router = DefaultRouter()

router.register(
    "events",
    AuditEventViewSet,
    basename="audit-event",
)

urlpatterns = router.urls