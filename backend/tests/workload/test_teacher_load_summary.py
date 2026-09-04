from decimal import Decimal

from django.test import TestCase

from apps.workload.services.teacher_load_summary import (
    TeacherLoadSummaryService,
)

from tests.factories import (
    AcademicYearFactory,
    PlannedWorkloadFactory,
    StaffEmploymentAcademicYearFactory,
    StaffEmploymentFactory,
    WorkloadDistributionFactory,
    WorkloadNormFactory,
)
from apps.workload.models import (WorkloadDistribution)


class TeacherLoadSummaryServiceTests(
    TestCase,
):
    def test_approved_hours_are_counted(
        self,
    ):
        academic_year = (
            AcademicYearFactory()
        )

        employment = (
            StaffEmploymentFactory()
        )

        StaffEmploymentAcademicYearFactory(
            staff_employment=employment,
            academic_year=academic_year,
        )

        WorkloadNormFactory(
            academic_year=academic_year,
            rate=employment.rate,
            has_academic_degree=(
                    employment.staff_member
                    .academic_degree_id
                    is not None
            ),
            has_academic_title=(
                    employment.staff_member
                    .academic_title_id
                    is not None
            ),
            annual_hours=Decimal("800.00"),
        )

        workload = (
            PlannedWorkloadFactory(
                academic_year=academic_year,
                teaching_department=(
                    employment.department
                ),
            )
        )

        distribution = (
            WorkloadDistributionFactory(
                planned_workload=workload,
                staff_employment=employment,
                allocated_hours=Decimal(
                    "30.00"
                ),
            )
        )

        distribution.status = WorkloadDistribution.Status.APPROVED

        distribution.save(
            update_fields=[
                "status",
            ]
        )

        result = (
            TeacherLoadSummaryService
            .build_for_employment(
                staff_employment=employment,
                academic_year_id=(
                    academic_year.pk
                ),
            )
        )

        self.assertEqual(
            result["approved_hours"],
            Decimal("30.00"),
        )

        self.assertEqual(
            result["remaining_hours"],
            Decimal("770.00"),
        )

        self.assertEqual(
            result["status"],
            "UNDERLOAD",
        )

    def test_draft_is_not_counted_as_approved(
        self,
    ):
        academic_year = (
            AcademicYearFactory()
        )

        employment = (
            StaffEmploymentFactory()
        )

        StaffEmploymentAcademicYearFactory(
            staff_employment=employment,
            academic_year=academic_year,
        )

        WorkloadNormFactory(
            academic_year=academic_year,
            rate=employment.rate,
            has_academic_degree=(
                    employment.staff_member
                    .academic_degree_id
                    is not None
            ),
            has_academic_title=(
                    employment.staff_member
                    .academic_title_id
                    is not None
            ),
            annual_hours=Decimal("800.00"),
        )

        workload = (
            PlannedWorkloadFactory(
                academic_year=academic_year,
                teaching_department=(
                    employment.department
                ),
            )
        )

        WorkloadDistributionFactory(
            planned_workload=workload,
            staff_employment=employment,
            allocated_hours=Decimal(
                "30.00"
            ),
            status=(
                WorkloadDistribution.Status.DRAFT
            ),
        )

        result = (
            TeacherLoadSummaryService
            .build_for_employment(
                staff_employment=employment,
                academic_year_id=(
                    academic_year.pk
                ),
            )
        )

        self.assertEqual(
            result["approved_hours"],
            Decimal("0.00"),
        )

        self.assertEqual(
            result["draft_hours"],
            Decimal("30.00"),
        )

    def test_overload_is_detected(
        self,
    ):
        academic_year = (
            AcademicYearFactory()
        )

        employment = (
            StaffEmploymentFactory()
        )

        StaffEmploymentAcademicYearFactory(
            staff_employment=employment,
            academic_year=academic_year,
        )

        WorkloadNormFactory(
            academic_year=academic_year,
            rate=employment.rate,
            has_academic_degree=(
                    employment.staff_member
                    .academic_degree_id
                    is not None
            ),
            has_academic_title=(
                    employment.staff_member
                    .academic_title_id
                    is not None
            ),
            annual_hours=Decimal("800.00"),
        )

        workload = (
            PlannedWorkloadFactory(
                academic_year=academic_year,
                teaching_department=(
                    employment.department
                ),
            )
        )

        distribution = (
            WorkloadDistributionFactory(
                planned_workload=workload,
                staff_employment=employment,
                allocated_hours=Decimal(
                    "801.00"
                ),
                status=(
                    WorkloadDistribution.Status.APPROVED
                ),
            )
        )

        result = (
            TeacherLoadSummaryService
            .build_for_employment(
                staff_employment=employment,
                academic_year_id=(
                    academic_year.pk
                ),
            )
        )

        self.assertEqual(
            result["status"],
            "OVERLOAD",
        )

        self.assertEqual(
            result["remaining_hours"],
            Decimal("-1.00"),
        )