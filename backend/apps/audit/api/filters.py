from django_filters import rest_framework as filters

from apps.audit.models import AuditEvent


class AuditEventFilter(filters.FilterSet):
    app_label = filters.CharFilter(
        field_name="content_type__app_label",
    )
    model = filters.CharFilter(
        field_name="content_type__model",
    )
    object_id = filters.CharFilter()
    actor = filters.NumberFilter(
        field_name="actor_id",
    )
    action = filters.ChoiceFilter(
        choices=AuditEvent.Action.choices,
    )

    university = filters.NumberFilter(
        field_name="university_id",
    )
    faculty = filters.NumberFilter(
        field_name="faculty_id",
    )
    department = filters.NumberFilter(
        field_name="department_id",
    )
    staff_member = filters.NumberFilter(
        field_name="staff_member_id",
    )
    academic_year = filters.NumberFilter(
        field_name="academic_year_id",
    )

    created_from = filters.IsoDateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )
    created_until = filters.IsoDateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )

    class Meta:
        model = AuditEvent
        fields = (
            "app_label",
            "model",
            "object_id",
            "actor",
            "action",
            "university",
            "faculty",
            "department",
            "staff_member",
            "academic_year",
            "created_from",
            "created_until",
        )