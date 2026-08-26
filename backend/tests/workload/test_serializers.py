from decimal import Decimal

from django.test import TestCase

from apps.workload.api.serializers import (
    ApproveSelectedDistributionsSerializer,
    CancelSelectedDistributionsSerializer,
    RestoreDistributionSerializer,
    TransferDistributionHoursSerializer,
    WorkloadDistributionCreateSerializer,
    WorkloadDistributionPartialUpdateSerializer,
    WorkloadDistributionSerializer,
)
from apps.workload.models import (
    WorkloadDistribution,
)
from tests.factories import (
    PlannedWorkloadFactory,
    StaffEmploymentAcademicYearFactory,
    StaffEmploymentFactory,
    WorkloadDistributionFactory,
)


class WorkloadDistributionSerializerTests(
    TestCase
):
    def test_output_contains_related_fields(
        self,
    ):
        distribution = (
            WorkloadDistributionFactory()
        )

        serializer = (
            WorkloadDistributionSerializer(
                distribution
            )
        )

        self.assertIn(
            "semester_number",
            serializer.data,
        )

        self.assertIn(
            "season",
            serializer.data,
        )

        self.assertIn(
            "group_semester",
            serializer.data,
        )

        self.assertIn(
            "student_group",
            serializer.data,
        )

        self.assertIn(
            "student_group_code",
            serializer.data,
        )

        self.assertIn(
            "workload_scope",
            serializer.data,
        )
        self.assertEqual(
            serializer.data["workload_scope"],
            "stream",
        )

        self.assertIsNone(
            serializer.data["group_semester"],
        )
        self.assertIsNone(
            serializer.data["student_group"],
        )
        self.assertIsNone(
            serializer.data["student_group_code"],
        )

        self.assertEqual(
            serializer.data["teacher"],
            distribution.staff_employment.staff_member_id,
        )
        self.assertEqual(
            serializer.data["department_name"],
            distribution.planned_workload.teaching_department.name_ru,
        )
        self.assertEqual(
            Decimal(serializer.data["planned_total_hours"]),
            distribution.planned_workload.total_hours,
        )


        self.assertEqual(
            serializer.data["teacher"],
            (
                distribution.staff_employment
                .staff_member_id
            ),
        )
        self.assertEqual(
            serializer.data["department_name"],
            (
                distribution.planned_workload
                .teaching_department
                .name_ru
            ),
        )
        self.assertEqual(
            Decimal(
                serializer.data[
                    "planned_total_hours"
                ]
            ),
            (
                distribution.planned_workload
                .total_hours
            ),
        )

    def test_approved_distribution_cannot_change_hours(
        self,
    ):
        distribution = (
            WorkloadDistributionFactory(
                status=(
                    WorkloadDistribution
                    .Status
                    .APPROVED
                ),
            )
        )

        serializer = (
            WorkloadDistributionPartialUpdateSerializer(
                distribution,
                data={
                    "allocated_hours": "20.00",
                },
                partial=True,
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )

    def test_cancelled_distribution_cannot_be_edited(
        self,
    ):
        distribution = (
            WorkloadDistributionFactory(
                status=(
                    WorkloadDistribution
                    .Status
                    .CANCELLED
                ),
            )
        )

        serializer = (
            WorkloadDistributionPartialUpdateSerializer(
                distribution,
                data={
                    "notes": "Изменение",
                },
                partial=True,
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )


class DistributionCreateSerializerTests(
    TestCase
):
    def test_valid_distribution(self):
        planned = PlannedWorkloadFactory(
            total_hours=Decimal("100.00"),
        )

        employment = StaffEmploymentFactory(
            department=(
                planned.teaching_department
            ),
        )

        StaffEmploymentAcademicYearFactory(
            staff_employment=employment,
            academic_year=planned.academic_year,
        )

        serializer = (
            WorkloadDistributionCreateSerializer(
                data={
                    "planned_workload": planned.pk,
                    "staff_employment": (
                        employment.pk
                    ),
                    "allocated_hours": "30.00",
                    "notes": "",
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_over_distribution_rejected(self):
        planned = PlannedWorkloadFactory(
            total_hours=Decimal("100.00"),
        )

        WorkloadDistributionFactory(
            planned_workload=planned,
            allocated_hours=Decimal("90.00"),
        )

        employment = StaffEmploymentFactory(
            department=(
                planned.teaching_department
            ),
        )

        StaffEmploymentAcademicYearFactory(
            staff_employment=employment,
            academic_year=planned.academic_year,
        )

        serializer = (
            WorkloadDistributionCreateSerializer(
                data={
                    "planned_workload": planned.pk,
                    "staff_employment": (
                        employment.pk
                    ),
                    "allocated_hours": "20.00",
                }
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "allocated_hours",
            serializer.errors,
        )


class WorkloadActionSerializerTests(
    TestCase
):
    def test_approve_selected_removes_duplicates(
        self,
    ):
        serializer = (
            ApproveSelectedDistributionsSerializer(
                data={
                    "ids": [3, 1, 3, 2, 1],
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )
        self.assertEqual(
            serializer.validated_data["ids"],
            [3, 1, 2],
        )

    def test_cancel_selected_requires_reason(
        self,
    ):
        serializer = (
            CancelSelectedDistributionsSerializer(
                data={
                    "ids": [1, 2],
                    "reason": "   ",
                }
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "reason",
            serializer.errors,
        )

    def test_restore_requires_reason(self):
        serializer = RestoreDistributionSerializer(
            data={
                "reason": "   ",
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "reason",
            serializer.errors,
        )

    def test_transfer_requires_positive_hours(
        self,
    ):
        serializer = (
            TransferDistributionHoursSerializer(
                data={
                    "target_staff_employment": 1,
                    "transfer_hours": "0.00",
                    "reason": "Перенос",
                }
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "transfer_hours",
            serializer.errors,
        )