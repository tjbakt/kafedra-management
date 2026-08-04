from django.test import SimpleTestCase

from apps.audit.api.filters import (
    AuditEventFilter,
)


class AuditEventFilterTests(
    SimpleTestCase
):
    def test_required_core_filters(self):
        filters = set(
            AuditEventFilter.base_filters
        )

        required = {
            'academic_year', 'action', 'actor', 'app_label', 'created_from', 'created_until', 'department', 'faculty',
            'model', 'object_id', 'staff_member', 'university',
        }

        self.assertTrue(
            required.issubset(filters),
            (
                "В AuditEventFilter отсутствуют "
                f"обязательные фильтры: "
                f"{sorted(required - filters)}. "
                f"Фактические фильтры: "
                f"{sorted(filters)}"
            ),
        )