from datetime import date
from decimal import Decimal

from django.core.exceptions import (
    ValidationError,
)
from django.test import TestCase

from apps.individual_plan.models import (
    IndividualPlan,
    IndividualPlanItem,
    IndividualPlanSection,
    IndividualPlanTeachingWorkload,
)
from apps.workload.models import (
    WorkloadDistribution,
)
from tests.factories import (
    AcademicSemesterFactory,
    AcademicYearFactory,
    IndividualActivityTypeFactory,
    IndividualPlanFactory,
    IndividualPlanItemFactory,
    IndividualPlanSectionFactory,
    IndividualPlanTeachingWorkloadFactory,
    StaffEmploymentFactory,
    StaffPositionFactory,
    WorkloadDistributionFactory,
)


class IndividualPlanModelTests(TestCase):
    def test_string_representation(self):
        plan = IndividualPlanFactory()

        self.assertEqual(
            str(plan),
            (
                f"{plan.teacher_name} — "
                f"{plan.academic_year}"
            ),
        )

    def test_properties(self):
        plan = IndividualPlanFactory()

        self.assertEqual(
            plan.staff_member,
            plan.staff_employment.staff_member,
        )
        self.assertEqual(
            plan.department,
            plan.staff_employment.department,
        )

    def test_inactive_employment_rejected(self):
        plan = IndividualPlan(
            staff_employment=(
                StaffEmploymentFactory(
                    is_active=False,
                )
            ),
            academic_year=AcademicYearFactory(),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            plan.full_clean()

        self.assertIn(
            "staff_employment",
            context.exception.message_dict,
        )

    def test_non_teaching_position_rejected(
        self,
    ):
        plan = IndividualPlan(
            staff_employment=(
                StaffEmploymentFactory(
                    position=StaffPositionFactory(
                        is_teaching_position=False,
                    )
                )
            ),
            academic_year=AcademicYearFactory(),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            plan.full_clean()

        self.assertIn(
            "staff_employment",
            context.exception.message_dict,
        )

    def test_hours_and_completion(self):
        plan = IndividualPlanFactory()

        IndividualPlanItemFactory(
            individual_plan=plan,
            planned_hours=Decimal("20.00"),
            actual_hours=Decimal("10.00"),
            status=(
                IndividualPlanItem.Status.COMPLETED
            ),
            actual_completion_date=date.today(),
        )

        IndividualPlanItemFactory(
            individual_plan=plan,
            planned_hours=Decimal("30.00"),
            actual_hours=Decimal("30.00"),
            status=(
                IndividualPlanItem.Status.CONFIRMED
            ),
            actual_completion_date=date.today(),
            confirmed_by=plan.created_by,
        )

        self.assertEqual(
            plan.planned_hours,
            Decimal("50.00"),
        )
        self.assertEqual(
            plan.actual_hours,
            Decimal("40.00"),
        )
        self.assertEqual(
            plan.completion_percent,
            Decimal("80.00"),
        )


class IndividualPlanItemModelTests(
    TestCase
):
    def test_wrong_activity_section_rejected(
        self,
    ):
        section = IndividualPlanSectionFactory()
        other_activity = (
            IndividualActivityTypeFactory(
                section=IndividualPlanSectionFactory(
                    code=(
                        IndividualPlanSection
                        .Code
                        .SCIENTIFIC
                    ),
                    name_ru="Научная работа",
                    name_uz="Ilmiy ish",
                )
            )
        )

        item = IndividualPlanItemFactory.build(
            individual_plan=(
                IndividualPlanFactory()
            ),
            section=section,
            activity_type=other_activity,
            academic_semester=None,
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            item.full_clean()

        self.assertIn(
            "activity_type",
            context.exception.message_dict,
        )

    def test_wrong_academic_year_rejected(
        self,
    ):
        plan = IndividualPlanFactory()

        item = IndividualPlanItemFactory.build(
            individual_plan=plan,
            academic_semester=(
                AcademicSemesterFactory(
                    academic_year=(
                        AcademicYearFactory()
                    )
                )
            ),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            item.full_clean()

        self.assertIn(
            "academic_semester",
            context.exception.message_dict,
        )

    def test_invalid_dates_rejected(self):
        item = IndividualPlanItemFactory.build(
            individual_plan=(
                IndividualPlanFactory()
            ),
            academic_semester=None,
            planned_start_date=date(2026, 10, 1),
            planned_end_date=date(2026, 9, 1),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            item.full_clean()

        self.assertIn(
            "planned_end_date",
            context.exception.message_dict,
        )

    def test_completed_requires_date(self):
        item = IndividualPlanItemFactory.build(
            individual_plan=(
                IndividualPlanFactory()
            ),
            academic_semester=None,
            status=(
                IndividualPlanItem.Status.COMPLETED
            ),
            actual_completion_date=None,
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            item.full_clean()

        self.assertIn(
            "actual_completion_date",
            context.exception.message_dict,
        )

    def test_evidence_required(self):
        section = IndividualPlanSectionFactory()

        activity = IndividualActivityTypeFactory(
            section=section,
            requires_evidence=True,
        )

        item = IndividualPlanItemFactory.build(
            individual_plan=(
                IndividualPlanFactory()
            ),
            section=section,
            activity_type=activity,
            academic_semester=None,
            status=(
                IndividualPlanItem.Status.COMPLETED
            ),
            actual_completion_date=date.today(),
            evidence_url="",
            evidence_document="",
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            item.full_clean()

        self.assertIn(
            "evidence_document",
            context.exception.message_dict,
        )


class TeachingWorkloadLinkModelTests(
    TestCase
):
    def test_valid_link(self):
        link = (
            IndividualPlanTeachingWorkloadFactory()
        )

        link.full_clean()

    def test_unapproved_distribution_rejected(
        self,
    ):
        distribution = WorkloadDistributionFactory(
            status=(
                WorkloadDistribution.Status.DRAFT
            )
        )

        plan = IndividualPlanFactory(
            staff_employment=(
                distribution.staff_employment
            ),
            academic_year=(
                distribution.planned_workload
                .academic_year
            ),
        )

        item = IndividualPlanItemFactory(
            individual_plan=plan,
            academic_semester=(
                distribution.planned_workload
                .academic_semester
            ),
        )

        link = IndividualPlanTeachingWorkload(
            plan_item=item,
            workload_distribution=distribution,
            imported_hours=(
                distribution.allocated_hours
            ),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            link.full_clean()

        self.assertIn(
            "workload_distribution",
            context.exception.message_dict,
        )