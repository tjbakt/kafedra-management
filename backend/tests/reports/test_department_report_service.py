from decimal import Decimal

from django.test import TestCase

from apps.curriculum.models import (
    WorkloadType,
)
from apps.reports.exceptions import (
    ReportDataError,
)
from apps.reports.services.department_workload_report import (
    DepartmentWorkloadReportService,
)
from tests.factories import (
    CurriculumWorkloadFactory,
    PlannedWorkloadFactory,
    TeachingStreamFactory,
    TeachingStreamGroupFactory,
    WorkloadDistributionFactory,
    WorkloadTypeFactory,
)


class DepartmentWorkloadReportServiceTests(
    TestCase
):
    def create_planned(
        self,
        *,
        category,
        mode,
        base_hours,
        total_hours,
    ):
        workload_type = WorkloadTypeFactory(
            report_category=category,
            calculation_mode=mode,
        )

        curriculum_workload = (
            CurriculumWorkloadFactory(
                workload_type=workload_type,
                calculation_mode=mode,
                base_hours=Decimal(
                    base_hours
                ),
            )
        )

        stream = TeachingStreamFactory(
            curriculum_discipline=(
                curriculum_workload
                .curriculum_discipline
            ),
            curriculum_workload=(
                curriculum_workload
            ),
            teaching_department=(
                curriculum_workload
                .curriculum_discipline
                .teaching_department
            ),
        )

        planned = PlannedWorkloadFactory(
            teaching_stream=stream,
            curriculum_workload=(
                curriculum_workload
            ),
            academic_year=(
                stream.academic_year
            ),
            academic_semester=(
                stream.academic_semester
            ),
            teaching_department=(
                stream.teaching_department
            ),
            calculation_mode=mode,
            base_hours=Decimal(
                base_hours
            ),
            total_hours=Decimal(
                total_hours
            ),
        )

        return planned

    def test_per_group_allocation(self):
        planned = self.create_planned(
            category=(
                WorkloadType
                .ReportCategory
                .PRACTICE
            ),
            mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),
            base_hours="10.00",
            total_hours="20.00",
        )

        memberships = (
            TeachingStreamGroupFactory
            .create_batch(
                2,
                teaching_stream=(
                    planned.teaching_stream
                ),
            )
        )

        result = (
            DepartmentWorkloadReportService
            .allocate_hours_by_group(
                planned=planned,
                stream_groups=memberships,
                report_category=(
                    WorkloadType
                    .ReportCategory
                    .PRACTICE
                ),
            )
        )

        self.assertEqual(
            result[memberships[0].pk],
            Decimal("10.00"),
        )
        self.assertEqual(
            result[memberships[1].pk],
            Decimal("10.00"),
        )

    def test_per_student_allocation(self):
        planned = self.create_planned(
            category=(
                WorkloadType
                .ReportCategory
                .PRACTICE
            ),
            mode=(
                WorkloadType
                .CalculationMode
                .PER_STUDENT
            ),
            base_hours="0.50",
            total_hours="15.00",
        )

        membership = TeachingStreamGroupFactory(
            teaching_stream=(
                planned.teaching_stream
            )
        )

        membership.group_semester.students_count = (
            30
        )
        membership.group_semester.save(
            update_fields=("students_count",)
        )

        result = (
            DepartmentWorkloadReportService
            .allocate_hours_by_group(
                planned=planned,
                stream_groups=[membership],
                report_category=(
                    WorkloadType
                    .ReportCategory
                    .PRACTICE
                ),
            )
        )

        self.assertEqual(
            result[membership.pk],
            Decimal("15.00"),
        )

    def test_lecture_goes_to_first_group(
        self,
    ):
        planned = self.create_planned(
            category=(
                WorkloadType
                .ReportCategory
                .LECTURE
            ),
            mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),
            base_hours="30.00",
            total_hours="30.00",
        )

        memberships = (
            TeachingStreamGroupFactory
            .create_batch(
                2,
                teaching_stream=(
                    planned.teaching_stream
                ),
            )
        )

        result = (
            DepartmentWorkloadReportService
            .allocate_hours_by_group(
                planned=planned,
                stream_groups=memberships,
                report_category=(
                    WorkloadType
                    .ReportCategory
                    .LECTURE
                ),
            )
        )

        self.assertEqual(
            result[memberships[0].pk],
            Decimal("30.00"),
        )
        self.assertEqual(
            result[memberships[1].pk],
            Decimal("0.00"),
        )

    def test_mismatched_total_rejected(self):
        planned = self.create_planned(
            category=(
                WorkloadType
                .ReportCategory
                .PRACTICE
            ),
            mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),
            base_hours="10.00",
            total_hours="30.00",
        )

        memberships = (
            TeachingStreamGroupFactory
            .create_batch(
                2,
                teaching_stream=(
                    planned.teaching_stream
                ),
            )
        )

        with self.assertRaises(
            ReportDataError
        ):
            (
                DepartmentWorkloadReportService
                .allocate_hours_by_group(
                    planned=planned,
                    stream_groups=(
                        memberships
                    ),
                    report_category=(
                        WorkloadType
                        .ReportCategory
                        .PRACTICE
                    ),
                )
            )

    def test_teacher_names_only_approved(
        self,
    ):
        planned = self.create_planned(
            category=(
                WorkloadType
                .ReportCategory
                .LECTURE
            ),
            mode=(
                WorkloadType
                .CalculationMode
                .FIXED
            ),
            base_hours="30.00",
            total_hours="30.00",
        )

        approved = WorkloadDistributionFactory(
            planned_workload=planned,
            status="approved",
        )

        WorkloadDistributionFactory(
            planned_workload=planned,
            status="draft",
        )

        result = (
            DepartmentWorkloadReportService
            .get_teacher_names(planned)
        )

        self.assertEqual(
            result,
            {approved.teacher_name},
        )