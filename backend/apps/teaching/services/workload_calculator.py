from decimal import Decimal

from django.db import transaction

from apps.audit.models import AuditEvent
from apps.audit.services.audit_service import AuditService
from apps.curriculum.models import (
    CurriculumWorkload,
    WorkloadType,
)
from apps.teaching.models import (
    PlannedWorkload,
    TeachingStream,
)


class TeachingStreamWorkloadCalculator:
    """
    Рассчитывает всю нагрузку одного
    учебного потока.

    Поток относится ко всему учебному
    плану и одному semester_number.

    Для расчёта выбираются все активные
    дисциплины данного семестра и все
    активные виды нагрузки этих дисциплин.
    """

    def __init__(
        self,
        teaching_stream: TeachingStream,
    ):
        self.stream = teaching_stream

    def get_quantity(
        self,
        workload: CurriculumWorkload,
    ) -> Decimal:
        mode = workload.calculation_mode

        if (
            mode
            == WorkloadType.CalculationMode.FIXED
        ):
            return Decimal("1.00")

        if (
            mode
            == WorkloadType.CalculationMode.PER_GROUP
        ):
            return Decimal(
                self.stream.groups_count
            )

        if (
            mode
            == WorkloadType.CalculationMode.PER_SUBGROUP
        ):
            return Decimal(
                self.stream.subgroups_count
            )

        if (
            mode
            == WorkloadType.CalculationMode.PER_STUDENT
        ):
            return Decimal(
                self.stream.students_count
            )

        return Decimal("0.00")

    def get_curriculum_workloads(self):
        return (
            CurriculumWorkload.objects
            .filter(
                curriculum_discipline__curriculum=(
                    self.stream.curriculum
                ),
                curriculum_discipline__semester_number=(
                    self.stream.semester_number
                ),
                curriculum_discipline__is_active=True,
                curriculum_discipline__is_archived=False,
                is_active=True,
                is_archived=False,
                workload_type__is_active=True,
                workload_type__is_archived=False,
            )
            .select_related(
                "curriculum_discipline",
                "curriculum_discipline__discipline",
                "curriculum_discipline__teaching_department",
                "workload_type",
            )
            .order_by(
                "curriculum_discipline__discipline__name_ru",
                "workload_type__sort_order",
            )
        )

    @transaction.atomic
    def calculate(
        self,
        *,
        teaching_stream=None,
        user=None,
    ) -> list[PlannedWorkload]:
        stream = (
            teaching_stream
            or self.stream
        )

        groups_count = (
            stream.groups_count
        )

        subgroups_count = (
            stream.subgroups_count
        )

        students_count = (
            stream.students_count
        )

        if groups_count == 0:
            raise ValueError(
                "Нельзя рассчитать нагрузку "
                "потока без учебных групп."
            )

        workloads = list(
            self.get_curriculum_workloads()
        )

        if not workloads:
            raise ValueError(
                "В выбранном семестре "
                "учебного плана отсутствуют "
                "активные виды нагрузки."
            )

        calculated = []

        active_workload_ids = {
            workload.id
            for workload in workloads
        }

        for workload in workloads:
            quantity = self.get_quantity(
                workload
            )

            base_hours = (
                workload.base_hours
            )

            total_hours = (
                base_hours * quantity
            )

            discipline = (
                workload.curriculum_discipline
            )

            defaults = {
                "academic_year":
                    stream.academic_year,

                "academic_semester":
                    stream.academic_semester,

                "teaching_department":
                    discipline.teaching_department,

                "calculation_mode":
                    workload.calculation_mode,

                "base_hours":
                    base_hours,

                "calculation_quantity":
                    quantity,

                "total_hours":
                    total_hours,

                "groups_count":
                    groups_count,

                "subgroups_count":
                    subgroups_count,

                "students_count":
                    students_count,

                "status":
                    PlannedWorkload.Status.CALCULATED,

                "updated_by":
                    user,

                "is_archived":
                    False,

                "archived_at":
                    None,

                "archived_by":
                    None,
            }

            existing = (
                PlannedWorkload.all_objects
                .filter(
                    teaching_stream=stream,
                    curriculum_workload=workload,
                )
                .first()
            )

            old_values = {}

            if existing:
                old_values = {
                    "calculation_mode":
                        existing.calculation_mode,

                    "base_hours":
                        existing.base_hours,

                    "calculation_quantity":
                        existing.calculation_quantity,

                    "total_hours":
                        existing.total_hours,

                    "groups_count":
                        existing.groups_count,

                    "subgroups_count":
                        existing.subgroups_count,

                    "students_count":
                        existing.students_count,

                    "status":
                        existing.status,
                }

            planned_workload, created = (
                PlannedWorkload.all_objects
                .update_or_create(
                    teaching_stream=stream,
                    curriculum_workload=workload,
                    defaults=defaults,
                )
            )

            if created:
                planned_workload.created_by = (
                    user
                )

                planned_workload.save(
                    update_fields=(
                        "created_by",
                    )
                )

            AuditService.log(
                instance=planned_workload,
                action=AuditEvent.Action.CALCULATE,
                actor=user,
                action_label=(
                    "Плановая нагрузка рассчитана"
                ),
                old_values=old_values,
                new_values={
                    "calculation_mode":
                        planned_workload.calculation_mode,

                    "base_hours":
                        planned_workload.base_hours,

                    "calculation_quantity":
                        planned_workload.calculation_quantity,

                    "total_hours":
                        planned_workload.total_hours,

                    "groups_count":
                        planned_workload.groups_count,

                    "subgroups_count":
                        planned_workload.subgroups_count,

                    "students_count":
                        planned_workload.students_count,

                    "status":
                        planned_workload.status,
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
                    "teaching_stream":
                        stream.pk,

                    "curriculum":
                        stream.curriculum_id,

                    "semester_number":
                        stream.semester_number,

                    "curriculum_workload":
                        workload.pk,
                },
            )

            calculated.append(
                planned_workload
            )

        #
        # Если вид нагрузки был удалён
        # из учебного плана после
        # предыдущего расчёта,
        # соответствующую старую строку
        # больше не считаем актуальной.
        #
        stale_queryset = (
            PlannedWorkload.objects
            .filter(
                teaching_stream=stream,
            )
            .exclude(
                curriculum_workload_id__in=(
                    active_workload_ids
                )
            )
        )

        for stale in stale_queryset:
            stale.archive(user=user)

        stream.status = (
            TeachingStream.Status.CALCULATED
        )

        stream.updated_by = user

        stream.save(
            update_fields=(
                "status",
                "updated_by",
                "updated_at",
            )
        )

        return calculated