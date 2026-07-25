from django.contrib import admin

from apps.individual_plan.models import (
    IndividualActivityType,
    IndividualPlan,
    IndividualPlanItem,
    IndividualPlanSection,
    IndividualPlanTeachingWorkload,
)


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


@admin.register(IndividualPlanSection)
class IndividualPlanSectionAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name_ru",
        "is_hourly",
        "is_active",
        "sort_order",
        "is_archived",
    )
    list_filter = (
        "is_hourly",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
    )


@admin.register(IndividualActivityType)
class IndividualActivityTypeAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name_ru",
        "section",
        "default_hours",
        "requires_evidence",
        "is_active",
    )
    list_filter = (
        "section",
        "requires_evidence",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
    )
    autocomplete_fields = (
        "section",
    )


class IndividualPlanItemInline(admin.TabularInline):
    model = IndividualPlanItem
    extra = 0
    fields = (
        "section",
        "activity_type",
        "academic_semester",
        "title",
        "planned_hours",
        "actual_hours",
        "status",
    )
    autocomplete_fields = (
        "section",
        "activity_type",
        "academic_semester",
    )


@admin.register(IndividualPlan)
class IndividualPlanAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "teacher_name",
        "academic_year",
        "department",
        "status",
        "planned_hours",
        "actual_hours",
        "is_archived",
    )
    list_filter = (
        "academic_year",
        "staff_employment__department",
        "status",
        "is_archived",
    )
    search_fields = (
        "staff_employment__staff_member__personnel_number",
        "staff_employment__staff_member__last_name",
        "staff_employment__staff_member__first_name",
    )
    autocomplete_fields = (
        "staff_employment",
        "academic_year",
        "approved_by",
    )
    inlines = (
        IndividualPlanItemInline,
    )


@admin.register(IndividualPlanItem)
class IndividualPlanItemAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "title",
        "individual_plan",
        "section",
        "planned_hours",
        "actual_hours",
        "status",
        "actual_completion_date",
    )
    list_filter = (
        "individual_plan__academic_year",
        "section",
        "status",
        "is_archived",
    )
    search_fields = (
        "title",
        "description",
        "individual_plan__staff_employment__"
        "staff_member__last_name",
    )
    autocomplete_fields = (
        "individual_plan",
        "section",
        "activity_type",
        "academic_semester",
        "confirmed_by",
    )


@admin.register(IndividualPlanTeachingWorkload)
class IndividualPlanTeachingWorkloadAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "plan_item",
        "workload_distribution",
        "imported_hours",
        "is_archived",
    )
    search_fields = (
        "plan_item__title",
        "workload_distribution__staff_employment__"
        "staff_member__last_name",
    )
    autocomplete_fields = (
        "plan_item",
        "workload_distribution",
    )