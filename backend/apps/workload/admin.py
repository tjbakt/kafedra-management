from django.contrib import admin

from apps.workload.models import WorkloadDistribution


class ArchiveAdminMixin:
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "is_archived",
        "archived_at",
        "archived_by",
    )

    def get_queryset(self, request):
        return self.model.all_objects.all()


@admin.register(WorkloadDistribution)
class WorkloadDistributionAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "planned_workload",
        "teacher_name",
        "staff_employment",
        "allocated_hours",
        "status",
        "approved_at",
        "is_archived",
    )
    list_filter = (
        "planned_workload__academic_year",
        "planned_workload__academic_semester",
        "planned_workload__teaching_department",
        "staff_employment__position",
        "status",
        "is_archived",
    )
    search_fields = (
        "staff_employment__staff_member__personnel_number",
        "staff_employment__staff_member__last_name",
        "staff_employment__staff_member__first_name",
        "planned_workload__teaching_stream__code",
        "planned_workload__teaching_stream__"
        "curriculum_discipline__discipline__name_ru",
    )
    autocomplete_fields = (
        "planned_workload",
        "staff_employment",
        "approved_by",
    )
    readonly_fields = (
        *ArchiveAdminMixin.readonly_fields,
        "approved_at",
        "approved_by",
    )