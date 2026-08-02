from unittest.mock import patch

from django.test import TestCase

from apps.academics.exceptions import (
    AcademicYearClosingError,
)
from apps.academics.models import AcademicYear
from apps.academics.services.academic_year_closing_service import (
    AcademicYearClosingService,
)
from apps.audit.models import AuditEvent
from tests.factories import (
    AcademicYearFactory,
    UserFactory,
)


READY_RESULT = {
    "academic_year": 1,
    "academic_year_name": "2026/2027",
    "department_ids": [],
    "ready_to_close": True,
    "status": "ready",
    "message": "Год готов.",
    "summary": {
        "planned_workloads_count": 0,
        "distributions_count": 0,
        "year_staff_records_count": 0,
        "blocking_issues_count": 0,
        "warnings_count": 0,
        "blocking_issues_by_type": {},
        "warnings_by_type": {},
    },
    "blocking_issues": [],
    "warnings": [],
}


NOT_READY_RESULT = {
    **READY_RESULT,
    "ready_to_close": False,
    "status": "not_ready",
    "message": "Год не готов.",
    "summary": {
        **READY_RESULT["summary"],
        "blocking_issues_count": 1,
    },
    "blocking_issues": [
        {
            "severity": "error",
            "issue_type": "unallocated_workload",
            "message": "Есть нераспределённая нагрузка.",
            "details": {},
        }
    ],
}


class AcademicYearClosingServiceTests(
    TestCase
):
    def setUp(self):
        self.user = UserFactory()
        self.academic_year = (
            AcademicYearFactory(
                start_year=2026,
                end_year=2027,
                is_current=True,
            )
        )

    @patch(
        (
            "apps.academics.services."
            "academic_year_closing_service."
            "AcademicYearClosingReadinessService."
            "ensure_ready"
        ),
        return_value=READY_RESULT,
    )
    def test_close_year(
        self,
        mocked_readiness,
    ):
        closed_year, readiness = (
            AcademicYearClosingService.close(
                academic_year=(
                    self.academic_year
                ),
                user=self.user,
                comment="  Завершено  ",
            )
        )

        closed_year.refresh_from_db()

        self.assertEqual(
            closed_year.status,
            AcademicYear.Status.CLOSED,
        )
        self.assertFalse(
            closed_year.is_active
        )
        self.assertFalse(
            closed_year.is_current
        )
        self.assertEqual(
            closed_year.closed_by,
            self.user,
        )
        self.assertEqual(
            closed_year.closing_comment,
            "Завершено",
        )
        self.assertIsNotNone(
            closed_year.closed_at
        )
        self.assertTrue(
            readiness["ready_to_close"]
        )

        mocked_readiness.assert_called_once()

        self.assertTrue(
            AuditEvent.objects.filter(
                actor=self.user,
                action=(
                    AuditEvent.Action.COMPLETE
                ),
            ).exists()
        )

    @patch(
        (
            "apps.academics.services."
            "academic_year_closing_service."
            "AcademicYearClosingReadinessService."
            "ensure_ready"
        ),
        return_value=NOT_READY_RESULT,
    )
    def test_not_ready_year_is_rejected(
        self,
        mocked_readiness,
    ):
        with self.assertRaises(
            AcademicYearClosingError
        ) as context:
            AcademicYearClosingService.close(
                academic_year=(
                    self.academic_year
                ),
                user=self.user,
            )

        self.assertEqual(
            context.exception.code,
            "academic_year_not_ready",
        )

        self.academic_year.refresh_from_db()

        self.assertEqual(
            self.academic_year.status,
            AcademicYear.Status.OPEN,
        )

    def test_already_closed_year_is_rejected(
        self,
    ):
        academic_year = (
            AcademicYearFactory.closed(
                user=self.user
            )
        )

        with self.assertRaises(
            AcademicYearClosingError
        ) as context:
            AcademicYearClosingService.close(
                academic_year=academic_year,
                user=self.user,
            )

        self.assertEqual(
            context.exception.code,
            "academic_year_already_closed",
        )

    def test_reopen_year(self):
        academic_year = (
            AcademicYearFactory.closed(
                user=self.user,
                closing_comment="Закрыто",
            )
        )

        reopened = (
            AcademicYearClosingService.reopen(
                academic_year=academic_year,
                user=self.user,
                reason="  Исправление нагрузки  ",
            )
        )

        reopened.refresh_from_db()

        self.assertEqual(
            reopened.status,
            AcademicYear.Status.OPEN,
        )
        self.assertTrue(
            reopened.is_active
        )
        self.assertFalse(
            reopened.is_current
        )
        self.assertIsNone(
            reopened.closed_at
        )
        self.assertIsNone(
            reopened.closed_by
        )
        self.assertEqual(
            reopened.reopened_by,
            self.user,
        )
        self.assertEqual(
            reopened.reopening_reason,
            "Исправление нагрузки",
        )

        self.assertTrue(
            AuditEvent.objects.filter(
                actor=self.user,
                action=(
                    AuditEvent.Action.RESTORE
                ),
            ).exists()
        )

    def test_reopen_requires_reason(self):
        academic_year = (
            AcademicYearFactory.closed(
                user=self.user
            )
        )

        with self.assertRaises(
            AcademicYearClosingError
        ) as context:
            AcademicYearClosingService.reopen(
                academic_year=academic_year,
                user=self.user,
                reason=" ",
            )

        self.assertEqual(
            context.exception.code,
            "reopening_reason_required",
        )

    def test_open_year_cannot_be_reopened(self):
        with self.assertRaises(
            AcademicYearClosingError
        ) as context:
            AcademicYearClosingService.reopen(
                academic_year=(
                    self.academic_year
                ),
                user=self.user,
                reason="Причина",
            )

        self.assertEqual(
            context.exception.code,
            "academic_year_already_open",
        )

    def test_ensure_open_rejects_closed_year(
        self,
    ):
        academic_year = (
            AcademicYearFactory.closed(
                user=self.user
            )
        )

        with self.assertRaises(
            AcademicYearClosingError
        ) as context:
            AcademicYearClosingService.ensure_open(
                academic_year=academic_year
            )

        self.assertEqual(
            context.exception.code,
            "academic_year_closed",
        )