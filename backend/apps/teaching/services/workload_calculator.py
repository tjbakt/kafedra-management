from decimal import Decimal

from django.db import transaction

from apps.audit.models import AuditEvent
from apps.audit.services.audit_service import (
    AuditService,
)

from apps.curriculum.models import (
    AcademicYearWorkloadNorm,
    CurriculumWorkload,
    WorkloadType,
)

from apps.teaching.models import (
    PlannedWorkload,
    TeachingStream,
)


class TeachingStreamWorkloadCalculator:
    def __init__(
        self,
        teaching_stream: TeachingStream,
    ):
        self.stream = teaching_stream

    def get_base_hours(
        self,
        workload: CurriculumWorkload,
    ) -> Decimal:
        workload_type = (
            workload.workload_type
        )

        if (
            not workload_type
            .uses_annual_norm
        ):
            return (
                workload.base_hours
            )

        norm = (
            AcademicYearWorkloadNorm
            .objects
            .filter(
                academic_year=(
                    self.stream
                    .academic_year
                ),
                workload_type=(
                    workload_type
                ),
                is_active=True,
                is_archived=False,
            )
            .first()
        )

        if not norm:
            raise ValueError(
                (
                    "Для учебного года "
                    f"{self.stream.academic_year} "
                    "не задана норма "
                    "для вида работы "
                    f"«{workload_type.name_ru}»."
                )
            )

        return norm.coefficient

    def get_curriculum_workloads(
        self,
    ):
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

                workload_type__is_teaching_load=True,
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
                "workload_type__id",
            )
        )

    def is_stream_level(
        self,
        workload: CurriculumWorkload,
    ) -> bool:
        return (
            workload
            .workload_type
            .code
            ==
            WorkloadType
            .Code
            .LECTURE
        )

    def get_group_quantity(
        self,
        workload: CurriculumWorkload,
        group_semester,
    ) -> Decimal:
        workload_type = (
            workload.workload_type
        )

        #
        # Квалификационная /
        # научная практика:
        #
        # коэффициент часов
        # за одну неделю
        # × фактическое число недель
        # конкретной группы.
        #
        if (
            workload_type
            .uses_weekly_norm
        ):
            return Decimal(
                group_semester
                .weeks_count
            )

        mode = (
            workload
            .calculation_mode
        )

        if (
            mode
            ==
            WorkloadType
            .CalculationMode
            .FIXED
        ):
            return Decimal("1.00")

        if (
            mode
            ==
            WorkloadType
            .CalculationMode
            .PER_GROUP
        ):
            return Decimal("1.00")

        if (
            mode
            ==
            WorkloadType
            .CalculationMode
            .PER_SUBGROUP
        ):
            return Decimal(
                group_semester
                .subgroup_count
            )

        if (
            mode
            ==
            WorkloadType
            .CalculationMode
            .PER_STUDENT
        ):
            return Decimal(
                group_semester
                .students_count
            )

        return Decimal("0.00")

    @staticmethod
    def snapshot(
        planned_workload:
            PlannedWorkload,
    ) -> dict:
        return {
            "group_semester": planned_workload.group_semester_id,
            "calculation_mode": planned_workload.calculation_mode,
            "base_hours": planned_workload.base_hours,
            "calculation_quantity": planned_workload.calculation_quantity,
            "total_hours": planned_workload.total_hours,

            "groups_count":
                planned_workload
                .groups_count,

            "subgroups_count":
                planned_workload
                .subgroups_count,

            "students_count":
                planned_workload
                .students_count,

            "status":
                planned_workload
                .status,
        }

    def log_calculation(
        self,
        *,
        planned_workload:
            PlannedWorkload,
        old_values: dict,
        user,
    ) -> None:
        new_values = (
            self.snapshot(
                planned_workload
            )
        )

        changed_fields = [
            field_name
            for field_name,
            value
            in new_values.items()
            if (
                old_values.get(
                    field_name
                )
                != value
            )
        ]

        AuditService.log(
            instance=(
                planned_workload
            ),

            action=(
                AuditEvent
                .Action
                .CALCULATE
            ),

            actor=user,

            action_label=(
                "Плановая нагрузка "
                "рассчитана"
            ),

            old_values=(
                old_values
            ),

            new_values=(
                new_values
            ),

            changed_fields=(
                changed_fields
            ),

            metadata={
                "teaching_stream":
                    self.stream.pk,

                "curriculum":
                    self.stream
                    .curriculum_id,

                "semester_number":
                    self.stream
                    .semester_number,

                "curriculum_workload":
                    planned_workload
                    .curriculum_workload_id,

                "group_semester":
                    planned_workload
                    .group_semester_id,
            },
        )

    def save_planned_workload(
        self,
        *,
        workload:
            CurriculumWorkload,
        group_semester,
        quantity: Decimal,
        base_hours: Decimal,
        user,
    ) -> PlannedWorkload:
        stream = self.stream

        discipline = (
            workload
            .curriculum_discipline
        )

        existing = (
            PlannedWorkload
            .all_objects
            .filter(
                teaching_stream=(
                    stream
                ),

                curriculum_workload=(
                    workload
                ),

                group_semester=(
                    group_semester
                ),
            )
            .first()
        )

        old_values = (
            self.snapshot(
                existing
            )
            if existing
            else {}
        )

        if group_semester is None:
            groups_count = (
                stream.groups_count
            )

            subgroups_count = (
                stream.subgroups_count
            )

            students_count = (
                stream.students_count
            )
        else:
            groups_count = 1

            subgroups_count = (
                group_semester
                .subgroup_count
            )

            students_count = (
                group_semester
                .students_count
            )

        planned_workload, created = (
            PlannedWorkload
            .all_objects
            .update_or_create(
                teaching_stream=(
                    stream
                ),

                curriculum_workload=(
                    workload
                ),

                group_semester=(
                    group_semester
                ),

                defaults={
                    "academic_year":
                        stream
                        .academic_year,

                    "academic_semester":
                        stream
                        .academic_semester,

                    "teaching_department":
                        discipline
                        .teaching_department,

                    "calculation_mode":
                        workload
                        .calculation_mode,

                    "base_hours":
                        base_hours,

                    "calculation_quantity":
                        quantity,

                    "total_hours":
                        (
                            base_hours
                            * quantity
                        ),

                    "groups_count":
                        groups_count,

                    "subgroups_count":
                        subgroups_count,

                    "students_count":
                        students_count,

                    "status":
                        PlannedWorkload
                        .Status
                        .CALCULATED,

                    "updated_by":
                        user,

                    "is_archived":
                        False,

                    "archived_at":
                        None,

                    "archived_by":
                        None,
                },
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

        self.log_calculation(
            planned_workload=(
                planned_workload
            ),

            old_values=(
                old_values
            ),

            user=user,
        )

        return planned_workload

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

        if stream is None:
            raise ValueError(
                "Учебный поток не указан."
            )

        self.stream = stream

        workloads = list(
            self
            .get_curriculum_workloads()
        )

        if not workloads:
            raise ValueError(
                (
                    "Для выбранного семестра "
                    "учебного плана нет видов "
                    "работ, включаемых "
                    "в нагрузку преподавателя."
                )
            )

        stream_groups = list(
            stream
            .stream_groups
            .filter(
                is_active=True,
                is_archived=False,
            )
            .select_related(
                "group_semester",
                "group_semester__group_curriculum",
                "group_semester__group_curriculum__student_group",
            )
            .order_by(
                "group_semester__group_curriculum__student_group__code",
            )
        )

        if not stream_groups:
            raise ValueError(
                (
                    "Нельзя рассчитать "
                    "плановую нагрузку "
                    "учебного потока "
                    "без учебных групп."
                )
            )

        calculated: list[PlannedWorkload] = []

        active_keys: set[
            tuple[int, int | None,]
        ] = set()

        for workload in workloads:
            base_hours = (
                self.get_base_hours(
                    workload
                )
            )

            #
            # ЛЕКЦИЯ:
            # одна строка на весь поток.
            #
            if self.is_stream_level(
                workload
            ):
                planned = (
                    self
                    .save_planned_workload(
                        workload=(
                            workload
                        ),

                        group_semester=None,

                        quantity=(
                            Decimal(
                                "1.00"
                            )
                        ),

                        base_hours=(
                            base_hours
                        ),

                        user=user,
                    )
                )

                active_keys.add(
                    (
                        workload.id,
                        None,
                    )
                )

                calculated.append(
                    planned
                )

                continue

            #
            # Все остальные работы:
            # отдельная строка
            # на каждую учебную группу.
            #
            for membership in (
                stream_groups
            ):
                group_semester = (
                    membership
                    .group_semester
                )

                quantity = (
                    self
                    .get_group_quantity(
                        workload,
                        group_semester,
                    )
                )

                planned = (
                    self
                    .save_planned_workload(
                        workload=(
                            workload
                        ),

                        group_semester=(
                            group_semester
                        ),

                        quantity=(
                            quantity
                        ),

                        base_hours=(
                            base_hours
                        ),

                        user=user,
                    )
                )

                active_keys.add(
                    (
                        workload.id,
                        group_semester.id,
                    )
                )

                calculated.append(
                    planned
                )

        #
        # Архивируем позиции,
        # которые существовали после
        # предыдущего расчёта,
        # но больше не должны
        # участвовать в текущем.
        #
        existing = (
            PlannedWorkload
            .objects
            .filter(
                teaching_stream=(
                    stream
                )
            )
        )

        for item in existing:
            key = (
                item
                .curriculum_workload_id,

                item
                .group_semester_id,
            )

            if key in active_keys:
                continue

            item.archive(
                user=user
            )

        old_status = (
            stream.status
        )

        stream.status = (
            TeachingStream
            .Status
            .CALCULATED
        )

        stream.updated_by = user

        stream.save(
            update_fields=(
                "status",
                "updated_by",
                "updated_at",
            )
        )

        if (
            old_status
            != stream.status
        ):
            AuditService.log_status_change(
                instance=stream,

                old_status=(
                    old_status
                ),

                new_status=(
                    stream.status
                ),

                actor=user,

                action=(
                    AuditEvent
                    .Action
                    .CALCULATE
                ),

                action_label=(
                    "Расчёт плановой "
                    "нагрузки потока"
                ),

                metadata={
                    "calculated_items":
                        len(
                            calculated
                        )
                },
            )

        return calculated