from datetime import date

from django.test import TestCase

from apps.individual_plan.api.serializers import (
    IndividualActivityTypeSerializer,
    IndividualPlanItemSerializer,
    IndividualPlanSerializer,
)
from apps.individual_plan.models import (
    IndividualPlan,
    IndividualPlanItem,
    IndividualPlanSection,
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
)


class IndividualActivitySerializerTests(
    TestCase
):
    def test_code_is_normalized(self):
        serializer = (
            IndividualActivityTypeSerializer(
                data={
                    "section": (
                        IndividualPlanSectionFactory()
                        .pk
                    ),
                    "code": " article-test ",
                    "name_ru": "Публикация статьи",
                    "name_uz": "Maqola nashri",
                    "default_hours": "20.00",
                    "requires_evidence": True,
                    "is_active": True,
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )
        self.assertEqual(
            serializer.validated_data["code"],
            "ARTICLE-TEST",
        )


class IndividualPlanSerializerTests(
    TestCase
):
    def test_valid_plan(self):
        serializer = IndividualPlanSerializer(
            data={
                "staff_employment": (
                    StaffEmploymentFactory().pk
                ),
                "academic_year": (
                    AcademicYearFactory().pk
                ),
                "teacher_notes": "",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_non_teaching_employment_rejected(
        self,
    ):
        employment = StaffEmploymentFactory(
            position=StaffPositionFactory(
                is_teaching_position=False,
            )
        )

        serializer = IndividualPlanSerializer(
            data={
                "staff_employment": employment.pk,
                "academic_year": (
                    AcademicYearFactory().pk
                ),
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "staff_employment",
            serializer.errors,
        )

    def test_approved_plan_cannot_be_edited(
        self,
    ):
        plan = IndividualPlanFactory(
            status=IndividualPlan.Status.APPROVED,
        )

        serializer = IndividualPlanSerializer(
            plan,
            data={
                "teacher_notes": "Изменение",
            },
            partial=True,
        )

        self.assertFalse(
            serializer.is_valid()
        )


class IndividualPlanItemSerializerTests(
    TestCase
):
    def test_wrong_section_rejected(self):
        section = IndividualPlanSectionFactory()

        activity = IndividualActivityTypeFactory(
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

        serializer = IndividualPlanItemSerializer(
            data={
                "individual_plan": (
                    IndividualPlanFactory().pk
                ),
                "section": section.pk,
                "activity_type": activity.pk,
                "title": "Работа",
                "planned_hours": "10.00",
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "activity_type",
            serializer.errors,
        )

    def test_wrong_semester_rejected(self):
        plan = IndividualPlanFactory()

        semester = AcademicSemesterFactory(
            academic_year=AcademicYearFactory(),
        )

        serializer = IndividualPlanItemSerializer(
            data={
                "individual_plan": plan.pk,
                "section": (
                    IndividualPlanSectionFactory()
                    .pk
                ),
                "academic_semester": semester.pk,
                "title": "Работа",
                "planned_hours": "10.00",
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "academic_semester",
            serializer.errors,
        )

    def test_completed_requires_date(self):
        serializer = IndividualPlanItemSerializer(
            data={
                "individual_plan": (
                    IndividualPlanFactory().pk
                ),
                "section": (
                    IndividualPlanSectionFactory()
                    .pk
                ),
                "title": "Работа",
                "planned_hours": "10.00",
                "status": (
                    IndividualPlanItem
                    .Status
                    .COMPLETED
                ),
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "actual_completion_date",
            serializer.errors,
        )

    def test_imported_hours_are_protected(
        self,
    ):
        link = (
            IndividualPlanTeachingWorkloadFactory()
        )

        serializer = IndividualPlanItemSerializer(
            link.plan_item,
            data={
                "planned_hours": "99.00",
            },
            partial=True,
        )

        self.assertFalse(
            serializer.is_valid()
        )