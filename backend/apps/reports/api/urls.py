from django.urls import path

from apps.reports.api.views import (
    DepartmentWorkloadExcelView,
    TeacherWorkloadExcelView,
)


app_name = "reports"


urlpatterns = [
    path(
        "teacher-workload/",
        TeacherWorkloadExcelView.as_view(),
        name="teacher-workload-excel",
    ),
    path(
        "department-workload/",
        DepartmentWorkloadExcelView.as_view(),
        name="department-workload-excel",
    ),
]