from decimal import Decimal

from django.db import transaction

from apps.curriculum.models import WorkloadType
from apps.teaching.models import (
    PlannedWorkload,
    TeachingStream,
)

from apps.audit.models import AuditEvent
from apps.audit.services.audit_service import AuditService


class TeachingStreamWorkloadCalculator:
    """
    Рассчитывает нагрузку одного учебного потока.
    """

    def __init__(self, teaching_stream: TeachingStream):
        self.stream = teaching_stream
        self.curriculum_workload = (
            teaching_stream.curriculum_workload
        )

    def get_quantity(self) -> Decimal:
        mode = self.curriculum_workload.calculation_mode

        if mode == WorkloadType.CalculationMode.FIXED:
            return Decimal("1.00")

        if mode == WorkloadType.CalculationMode.PER_GROUP:
            return Decimal(self.stream.groups_count)

        if mode == WorkloadType.CalculationMode.PER_SUBGROUP:
            return Decimal(self.stream.subgroups_count)

        if mode == WorkloadType.CalculationMode.PER_STUDENT:
            return Decimal(self.stream.students_count)

        return Decimal("0.00")

    @transaction.atomic
    def calculate(self, *,  teaching_stream, user=None) -> PlannedWorkload:
        groups_count = self.stream.groups_count
        subgroups_count = self.stream.subgroups_count
        students_count = self.stream.students_count

        if groups_count == 0:
            raise ValueError(
                "Нельзя рассчитать нагрузку потока без групп."
            )

        quantity = self.get_quantity()
        base_hours = self.curriculum_workload.base_hours
        total_hours = base_hours * quantity

        defaults = {
            "academic_year": self.stream.academic_year,
            "academic_semester": self.stream.academic_semester,
            "teaching_department": (
                self.stream.teaching_department
            ),
            "curriculum_workload": (
                self.curriculum_workload
            ),
            "calculation_mode": (
                self.curriculum_workload.calculation_mode
            ),
            "base_hours": base_hours,
            "calculation_quantity": quantity,
            "total_hours": total_hours,
            "groups_count": groups_count,
            "subgroups_count": subgroups_count,
            "students_count": students_count,
            "status": PlannedWorkload.Status.CALCULATED,
            "updated_by": user,
        }

        existing = PlannedWorkload.objects.filter(
            teaching_stream=teaching_stream,
        ).first()

        old_values = {}

        if existing:
            old_values = {
                "calculation_mode": existing.calculation_mode,
                "base_hours": existing.base_hours,
                "calculation_quantity": (
                    existing.calculation_quantity
                ),
                "total_hours": existing.total_hours,
                "groups_count": existing.groups_count,
                "subgroups_count": existing.subgroups_count,
                "students_count": existing.students_count,
                "status": existing.status,
            }

        planned_workload, created = (
            PlannedWorkload.all_objects.update_or_create(
                teaching_stream=self.stream,
                defaults=defaults,
            )
        )

        if created:
            planned_workload.created_by = user
            planned_workload.save(
                update_fields=("created_by",)
            )

        self.stream.status = (
            TeachingStream.Status.CALCULATED
        )
        self.stream.updated_by = user
        self.stream.save(
            update_fields=(
                "status",
                "updated_by",
                "updated_at",
            )
        )

        AuditService.log(
            instance=planned_workload,
            action=AuditEvent.Action.CALCULATE,
            actor=user,
            action_label="Плановая нагрузка рассчитана",
            old_values=old_values,
            new_values={
                "calculation_mode": (
                    planned_workload.calculation_mode
                ),
                "base_hours": planned_workload.base_hours,
                "calculation_quantity": (
                    planned_workload.calculation_quantity
                ),
                "total_hours": planned_workload.total_hours,
                "groups_count": planned_workload.groups_count,
                "subgroups_count": (
                    planned_workload.subgroups_count
                ),
                "students_count": (
                    planned_workload.students_count
                ),
                "status": planned_workload.status,
            },
            changed_fields=[
                "calculation_mode",
                "base_hours",
                "calculation_quantity",
                "total_hours",
                "groups_count",
                "subgroups_count",
                "students_count",
                "status",
            ],
            metadata={
                "teaching_stream": teaching_stream.pk,
            },
        )

        return planned_workload