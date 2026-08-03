from decimal import Decimal

import factory

from apps.workload.models import (
    WorkloadDistribution,
)
from tests.factories.staff import (
    StaffEmploymentAcademicYearFactory,
    StaffEmploymentFactory,
)
from tests.factories.teaching import (
    PlannedWorkloadFactory,
)


class WorkloadDistributionFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = WorkloadDistribution

    planned_workload = factory.SubFactory(
        PlannedWorkloadFactory,
        total_hours=Decimal("100.00"),
    )

    staff_employment = factory.LazyAttribute(
        lambda obj: StaffEmploymentFactory(
            department=(
                obj.planned_workload
                .teaching_department
            ),
            is_active=True,
            position__is_teaching_position=True,
            created_by=(
                obj.planned_workload.created_by
            ),
            updated_by=(
                obj.planned_workload.updated_by
            ),
        )
    )

    allocated_hours = Decimal("30.00")
    status = (
        WorkloadDistribution.Status.DRAFT
    )

    approved_at = None
    approved_by = None
    notes = ""

    created_by = factory.SelfAttribute(
        "planned_workload.created_by"
    )
    updated_by = factory.SelfAttribute(
        "planned_workload.updated_by"
    )

    @factory.post_generation
    def ensure_academic_year_record(
        self,
        create,
        extracted,
        **kwargs,
    ):
        if not create:
            return

        StaffEmploymentAcademicYearFactory._meta.model.objects.get_or_create(
            staff_employment=self.staff_employment,
            academic_year=(
                self.planned_workload.academic_year
            ),
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