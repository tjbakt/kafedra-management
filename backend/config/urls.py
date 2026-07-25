
from django.contrib import admin
from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        "api/v1/",
        include("apps.common.urls", namespace="common"),
    ),

    path(
        "api/v1/auth/",
        include(
            "apps.accounts.api.urls",
            namespace="accounts",
        ),
    ),

    path(
        "api/v1/organizations/",
        include("apps.organizations.api.urls"),
    ),

    path(
        "api/v1/academics/",
        include("apps.academics.api.urls"),
    ),

    path(
        "api/v1/staff/",
        include("apps.staff.api.urls"),
    ),

    path(
        "api/v1/curriculum/",
        include("apps.curriculum.api.urls"),
    ),

    path(
        "api/v1/teaching/",
        include("apps.teaching.api.urls"),
    ),

    path(
        "api/v1/workload/",
        include("apps.workload.api.urls"),
    ),

    path(
        "api/v1/individual-plans/",
        include("apps.individual_plan.api.urls"),
    ),

    path(
        "api/v1/access-control/",
        include("apps.access_control.api.urls"),
    ),

    path(
        "api/v1/audit/",
        include("apps.audit.api.urls"),
    ),

    path(
        "api/v1/notifications/",
        include("apps.notifications.api.urls"),
    ),

    path(
        "api/v1/reports/",
        include("apps.reports.api.urls"),
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
