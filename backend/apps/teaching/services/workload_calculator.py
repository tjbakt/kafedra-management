from decimal import Decimal

from django.db import transaction

from apps.audit.models import AuditEvent
from apps.audit.services.audit_service import AuditService
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
        workload:
            CurriculumWorkload,
    ) -> Decimal:
        workload_type = (
            workload.workload_type
        )

        #
        # Обычная аудиторная работа:
        # часы идут непосредственно
        # из учебного плана.
        #
        if (
            not workload_type
            .uses_annual_norm
        ):
            return (
                workload.base_hours
            )

        #
        # Годовая норма:
        # берём учебный год
        # РЕАЛЬНОГО ПОТОКА,
        # а не effective_academic_year
        # учебного плана.
        #
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
                    "не задана норма для вида "
                    f"«{workload_type.name_ru}»."
                )
            )

        return norm.coefficient

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
            )
        )

    def is_stream_level(
            self,
            workload:
            CurriculumWorkload,
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
            workload,
            group_semester,
    ):
        workload_type = (
            workload.workload_type
        )

        if (
                workload_type
                        .uses_weekly_norm
        ):
            return Decimal(
                group_semester
                .weeks_count
            )

        mode = (
            workload.calculation_mode
        )

        if (
                mode ==
                WorkloadType
                        .CalculationMode
                        .FIXED
        ):
            return Decimal("1.00")

        if (
                mode ==
                WorkloadType
                        .CalculationMode
                        .PER_GROUP
        ):
            return Decimal("1.00")

        if (
                mode ==
                WorkloadType
                        .CalculationMode
                        .PER_SUBGROUP
        ):
            return Decimal(
                group_semester
                .subgroup_count
            )

        if (
                mode ==
                WorkloadType
                        .CalculationMode
                        .PER_STUDENT
        ):
            return Decimal(
                group_semester
                .students_count
            )

        return Decimal("0.00")

    # def get_stream_quantity(
    #         self,
    #         workload,
    # ):
    #     if (
    #             workload.workload_type.code
    #             ==
    #             WorkloadType.Code.LECTURE
    #     ):
    #         return Decimal("1.00")
    #
    #     return Decimal("0.00")

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

        if not stream:
            raise ValueError(
                "Учебный поток не указан."
            )

        workloads = list(
            self.get_curriculum_workloads()
        )
        if not workloads:
            raise ValueError(
                (
                    "Для выбранного семестра "
                    "учебного плана нет видов "
                    "работ, включаемых в "
                    "нагрузку преподавателя."
                )
            )

        stream_groups = list(
            stream.stream_groups
            .filter(
                is_active=True,
                is_archived=False,
            )
            .select_related(
                "group_semester",
                "group_semester__group_curriculum",
                "group_semester__group_curriculum__student_group",
            )
        )

        if not stream_groups:
            raise ValueError(
                (
                    "Нельзя рассчитать "
                    "плановую нагрузку "
                    "учебного потока без "
                    "учебных групп."
                )
            )

        calculated = []

        active_keys = set()

        for workload in workloads:
            base_hours = (
                self.get_base_hours(
                    workload
                )
            )

            discipline = (
                workload
                .curriculum_discipline
            )

            if self.is_stream_level(
                    workload
            ):
                quantity = Decimal(
                    "1.00"
                )

                planned, _ = (
                    PlannedWorkload
                    .all_objects
                    .update_or_create(
                        teaching_stream=stream,

                        curriculum_workload=(
                            workload
                        ),

                        group_semester=None,

                        defaults={
                            "academic_year":
                                stream.academic_year,

                            "academic_semester":
                                stream.academic_semester,

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
                                base_hours
                                * quantity,

                            "groups_count":
                                stream.groups_count,

                            "subgroups_count":
                                stream.subgroups_count,

                            "students_count":
                                stream.students_count,

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

            for membership in stream_groups:
                group_semester = (
                    membership
                    .group_semester
                )

                quantity = (
                    self.get_group_quantity(
                        workload,
                        group_semester,
                    )
                )

                total_hours = (
                        base_hours
                        * quantity
                )

                planned, _ = (
                    PlannedWorkload
                    .all_objects
                    .update_or_create(
                        teaching_stream=stream,

                        curriculum_workload=(
                            workload
                        ),

                        group_semester=(
                            group_semester
                        ),

                        defaults={
                            "academic_year":
                                stream.academic_year,

                            "academic_semester":
                                stream.academic_semester,

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
                                total_hours,

                            "groups_count":
                                1,

                            "subgroups_count":
                                group_semester
                                .subgroup_count,

                            "students_count":
                                group_semester
                                .students_count,

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

                active_keys.add(
                    (
                        workload.id,
                        group_semester.id,
                    )
                )

                calculated.append(
                    planned
                )

        existing = (
            PlannedWorkload
            .objects
            .filter(
                teaching_stream=stream,
            )
        )

        for item in existing:
            key = (
                item.curriculum_workload_id,
                item.group_semester_id,
            )

            if key in active_keys:
                continue

            item.is_archived = True

            item.archived_by = user

            item.save(
                update_fields=(
                    "is_archived",
                    "archived_by",
                    "archived_at",
                    "updated_at",
                )
            )

        return calculated