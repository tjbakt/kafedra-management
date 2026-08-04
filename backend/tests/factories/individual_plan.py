from datetime import date
from decimal import Decimal

import factory

from apps.individual_plan.models import (
    IndividualActivityType,
    IndividualPlan,
    IndividualPlanItem,
    IndividualPlanSection,
    IndividualPlanTeachingWorkload,
)
from apps.workload.models import (
    WorkloadDistribution,
)

from tests.factories.staff import (
    StaffEmploymentAcademicYearFactory,
    StaffEmploymentFactory,
)
from tests.factories.workload import (
    WorkloadDistributionFactory,
)


class IndividualPlanSectionFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = IndividualPlanSection
        django_get_or_create = ("code",)

    code = IndividualPlanSection.Code.TEACHING
    name_ru = "Учебная работа"
    name_uz = "O‘quv ishlari"

    is_hourly = True
    is_active = True
    sort_order = 10

    created_by = factory.SubFactory(
        "tests.factories.accounts.UserFactory"
    )
    updated_by = factory.SelfAttribute(
        "created_by"
    )


class IndividualActivityTypeFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = IndividualActivityType

    section = factory.SubFactory(
        IndividualPlanSectionFactory,
    )

    code = factory.Sequence(
        lambda number: (
            f"ACTIVITY-{number:05d}"
        )
    )
    name_ru = factory.Sequence(
        lambda number: (
            f"Вид индивидуальной работы {number}"
        )
    )
    name_uz = factory.Sequence(
        lambda number: (
            f"Individual ish turi {number}"
        )
    )

    default_hours = Decimal("20.00")
    requires_evidence = False
    is_active = True
    sort_order = 0

    created_by = factory.SelfAttribute(
        "section.created_by"
    )
    updated_by = factory.SelfAttribute(
        "section.updated_by"
    )


class IndividualPlanFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = IndividualPlan

    staff_employment = factory.SubFactory(
        StaffEmploymentFactory,
        is_active=True,
        position__is_teaching_position=True,
    )

    academic_year = factory.SubFactory(
        "tests.factories.academics."
        "AcademicYearFactory"
    )

    status = IndividualPlan.Status.DRAFT

    submitted_at = None
    approved_at = None
    approved_by = None
    closed_at = None

    teacher_notes = ""
    reviewer_notes = ""

    created_by = factory.SelfAttribute(
        "staff_employment.created_by"
    )
    updated_by = factory.SelfAttribute(
        "staff_employment.updated_by"
    )

    @factory.post_generation
    def ensure_year_record(
        self,
        create,
        extracted,
        **kwargs,
    ):
        if not create:
            return

        StaffEmploymentAcademicYearFactory._meta.model.objects.get_or_create(
            staff_employment=self.staff_employment,
            academic_year=self.academic_year,
            defaults={
                "rate": self.staff_employment.rate,
                "academic_degree": (
                    self.staff_employment
                    .staff_member
                    .academic_degree
                ),
                "academic_title": (
                    self.staff_employment
                    .staff_member
                    .academic_title
                ),
                "is_active": True,
                "created_by": self.created_by,
                "updated_by": self.updated_by,
            },
        )

class IndividualPlanItemFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = IndividualPlanItem

    individual_plan = factory.SubFactory(
        IndividualPlanFactory,
    )

    section = factory.SubFactory(
        IndividualPlanSectionFactory,
    )

    # Не создаём activity_type автоматически:
    # его раздел должен совпадать с section.
    activity_type = None

    # Семестр необязателен. В нужных тестах
    # он передаётся явно.
    academic_semester = None

    title = factory.Sequence(
        lambda number: (
            f"Пункт индивидуального плана {number}"
        )
    )
    description = ""

    planned_hours = Decimal("20.00")
    actual_hours = Decimal("0.00")

    planned_start_date = None
    planned_end_date = None
    actual_completion_date = None

    expected_result = ""
    actual_result = ""

    evidence_url = ""
    evidence_document = ""

    status = IndividualPlanItem.Status.PLANNED

    confirmed_at = None
    confirmed_by = None

    teacher_comment = ""
    reviewer_comment = ""

    sort_order = 0

    created_by = factory.SelfAttribute(
        "individual_plan.created_by"
    )
    updated_by = factory.SelfAttribute(
        "individual_plan.updated_by"
    )

    @classmethod
    def completed(
        cls,
        *,
        actual_hours=Decimal("20.00"),
        actual_completion_date=None,
        **kwargs,
    ):
        return cls(
            status=(
                IndividualPlanItem
                .Status
                .COMPLETED
            ),
            actual_hours=actual_hours,
            actual_completion_date=(
                actual_completion_date
                or date.today()
            ),
            **kwargs,
        )

class IndividualPlanTeachingWorkloadFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = IndividualPlanTeachingWorkload

    workload_distribution = factory.SubFactory(
        WorkloadDistributionFactory,
        status=(
            WorkloadDistribution.Status.APPROVED
        ),
    )

    plan_item = factory.LazyAttribute(
        lambda obj: IndividualPlanItemFactory(
            individual_plan=IndividualPlanFactory(
                staff_employment=(
                    obj.workload_distribution
                    .staff_employment
                ),
                academic_year=(
                    obj.workload_distribution
                    .planned_workload
                    .academic_year
                ),
                created_by=(
                    obj.workload_distribution
                    .created_by
                ),
                updated_by=(
                    obj.workload_distribution
                    .updated_by
                ),
            ),
            section=IndividualPlanSectionFactory(
                code=(
                    IndividualPlanSection
                    .Code
                    .TEACHING
                ),
            ),
            academic_semester=(
                obj.workload_distribution
                .planned_workload
                .academic_semester
            ),
            planned_hours=(
                obj.workload_distribution
                .allocated_hours
            ),
        )
    )

    imported_hours = factory.LazyAttribute(
        lambda obj: (
            obj.workload_distribution
            .allocated_hours
        )
    )

    created_by = factory.SelfAttribute(
        "plan_item.created_by"
    )
    updated_by = factory.SelfAttribute(
        "plan_item.updated_by"
    )