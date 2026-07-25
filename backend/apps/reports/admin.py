from django.contrib import admin

from apps.reports.models import ExcelReportTemplate


@admin.register(ExcelReportTemplate)
class ExcelReportTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "template_type",
        "university",
        "version",
        "sheet_name",
        "is_active",
        "is_archived",
    )
    list_filter = (
        "template_type",
        "university",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "name",
        "description",
        "university__name_ru",
        "university__name_uz",
    )
    autocomplete_fields = (
        "university",
    )
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
        return self.model.all_objects.select_related(
            "university"
        )