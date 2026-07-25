from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Iterable

from django.db.models import Prefetch, QuerySet

from apps.curriculum.models import WorkloadType
from apps.reports.exceptions import ReportDataError
from apps.teaching.models import (
    PlannedWorkload,
    TeachingStreamGroup,
)
from apps.workload.models import WorkloadDistribution


ZERO_HOURS = Decimal("0.00")


class DepartmentWorkloadReportService:
    """
    Подготавливает строки отчёта
    «Общая нагрузка кафедры за учебный год».
    """

    @classmethod
    def get_planned_workloads(
        cls,
        *,
        department_id: int,
        academic_year_id: int,
    ) -> QuerySet[PlannedWorkload]:
        stream_groups = (
            TeachingStreamGroup.objects
            .filter(
                is_archived=False,
                is_active=True,
                group_semester__is_archived=False,
                group_semester__is_active=True,
                group_semester__group_curriculum__is_archived=False,
                group_semester__group_curriculum__is_active=True,
                group_semester__group_curriculum__student_group__is_archived=False,
                group_semester__group_curriculum__student_group__is_active=True,
            )
            .select_related(
                "group_semester",
                "group_semester__group_curriculum",
                "group_semester__group_curriculum__student_group",
                "group_semester__group_curriculum__student_group__faculty",
                "group_semester__group_curriculum__student_group__study_program",
                "group_semester__group_curriculum__student_group__study_program__education_level",
                "group_semester__group_curriculum__student_group__study_form",
            )
            .order_by(
                "group_semester__group_curriculum__student_group__code",
                "pk",
            )
        )

        approved_distributions = (
            WorkloadDistribution.objects
            .filter(
                is_archived=False,
                status=WorkloadDistribution.Status.APPROVED,
                staff_employment__is_archived=False,
                staff_employment__is_active=True,
            )
            .select_related(
                "staff_employment",
                "staff_employment__staff_member",
            )
            .order_by(
                "staff_employment__staff_member__last_name",
                "staff_employment__staff_member__first_name",
                "pk",
            )
        )

        return (
            PlannedWorkload.objects
            .filter(
                teaching_department_id=department_id,
                academic_year_id=academic_year_id,
                is_archived=False,
            )
            .exclude(
                status=PlannedWorkload.Status.CANCELLED,
            )
            .select_related(
                "academic_year",
                "academic_semester",
                "teaching_department",
                "teaching_stream",
                "teaching_stream__curriculum_discipline",
                "teaching_stream__curriculum_discipline__discipline",
                "teaching_stream__curriculum_discipline__curriculum",
                "teaching_stream__curriculum_discipline__curriculum__study_program",
                "teaching_stream__curriculum_discipline__curriculum__study_program__education_level",
                "teaching_stream__curriculum_discipline__curriculum__study_form",
                "curriculum_workload",
                "curriculum_workload__workload_type",
            )
            .prefetch_related(
                Prefetch(
                    "teaching_stream__stream_groups",
                    queryset=stream_groups,
                    to_attr="report_stream_groups",
                ),
                Prefetch(
                    "distributions",
                    queryset=approved_distributions,
                    to_attr="report_approved_distributions",
                ),
            )
            .order_by(
                "teaching_stream__curriculum_discipline__curriculum__study_program__code",
                "teaching_stream__curriculum_discipline__semester_number",
                "teaching_stream__curriculum_discipline__discipline__name_ru",
                "teaching_stream__code",
                "curriculum_workload__workload_type__sort_order",
            )
        )

    @classmethod
    def prepare_rows(
        cls,
        planned_workloads: Iterable[PlannedWorkload],
    ) -> list[dict]:
        rows: dict[tuple, dict] = {}

        for planned in planned_workloads:
            stream = planned.teaching_stream
            curriculum_discipline = stream.curriculum_discipline
            curriculum = curriculum_discipline.curriculum
            report_category = (
                planned.curriculum_workload
                .workload_type
                .report_category
            )

            stream_groups = list(
                getattr(
                    stream,
                    "report_stream_groups",
                    [],
                )
            )

            if not stream_groups:
                raise ReportDataError(
                    f"Поток «{stream.code}» не содержит "
                    "активных учебных групп."
                )

            stream_groups.sort(
                key=lambda membership: (
                    membership
                    .group_semester
                    .student_group
                    .code,
                    membership.pk,
                )
            )

            allocations = cls.allocate_hours_by_group(
                planned=planned,
                stream_groups=stream_groups,
                report_category=report_category,
            )

            teacher_names = cls.get_teacher_names(planned)

            for membership in stream_groups:
                group_semester = membership.group_semester
                student_group = group_semester.student_group

                key = (
                    curriculum.pk,
                    curriculum_discipline.pk,
                    group_semester.semester_number,
                    student_group.pk,
                )

                if key not in rows:
                    rows[key] = cls.create_empty_row(
                        planned=planned,
                        group_semester=group_semester,
                    )

                hours = allocations.get(
                    membership.pk,
                    ZERO_HOURS,
                )

                if hours <= ZERO_HOURS:
                    continue

                cls.add_workload_to_row(
                    row=rows[key],
                    report_category=report_category,
                    hours=hours,
                    teacher_names=teacher_names,
                )

        result = list(rows.values())

        for row in result:
            row["total_hours"] = cls.calculate_total_hours(
                row
            )

            row["lecture_teacher"] = cls.join_teacher_names(
                row["teachers"]["lecture"]
            )
            row["practice_teacher"] = cls.join_teacher_names(
                row["teachers"]["practice"]
            )
            row["laboratory_teacher"] = cls.join_teacher_names(
                row["teachers"]["laboratory"]
            )

            row.pop("teachers", None)

        return sorted(
            result,
            key=lambda row: (
                row["faculty"],
                row["study_form"],
                row["study_program_code"],
                row["course"],
                row["semester"],
                row["group"],
                row["discipline"],
            ),
        )

    @classmethod
    def allocate_hours_by_group(
        cls,
        *,
        planned: PlannedWorkload,
        stream_groups: list[TeachingStreamGroup],
        report_category: str,
    ) -> dict[int, Decimal]:
        total_hours = Decimal(
            planned.total_hours or ZERO_HOURS
        )
        base_hours = Decimal(
            planned.curriculum_workload.base_hours
            or ZERO_HOURS
        )
        calculation_mode = (
            planned.curriculum_workload.calculation_mode
        )

        allocations = {
            membership.pk: ZERO_HOURS
            for membership in stream_groups
        }

        if (
            report_category
            == WorkloadType.ReportCategory.LECTURE
        ):
            allocations[stream_groups[0].pk] = total_hours

        elif (
            calculation_mode
            == WorkloadType.CalculationMode.PER_GROUP
        ):
            for membership in stream_groups:
                allocations[membership.pk] = base_hours

        elif (
            calculation_mode
            == WorkloadType.CalculationMode.PER_SUBGROUP
        ):
            for membership in stream_groups:
                subgroup_count = Decimal(
                    membership
                    .group_semester
                    .subgroup_count
                    or 0
                )

                allocations[membership.pk] = (
                    base_hours * subgroup_count
                )

        elif (
            calculation_mode
            == WorkloadType.CalculationMode.PER_STUDENT
        ):
            for membership in stream_groups:
                students_count = Decimal(
                    membership
                    .group_semester
                    .students_count
                    or 0
                )

                allocations[membership.pk] = (
                    base_hours * students_count
                )

        elif (
            calculation_mode
            == WorkloadType.CalculationMode.FIXED
        ):
            allocations[stream_groups[0].pk] = total_hours

        else:
            raise ReportDataError(
                "Неизвестный способ расчёта нагрузки: "
                f"{calculation_mode}."
            )

        cls.validate_allocations(
            planned=planned,
            allocations=allocations,
        )

        return allocations

    @staticmethod
    def validate_allocations(
        *,
        planned: PlannedWorkload,
        allocations: dict[int, Decimal],
    ) -> None:
        expected = Decimal(
            planned.total_hours or ZERO_HOURS
        ).quantize(Decimal("0.01"))

        actual = sum(
            allocations.values(),
            ZERO_HOURS,
        ).quantize(Decimal("0.01"))

        if actual != expected:
            raise ReportDataError(
                f"Поток «{planned.teaching_stream.code}»: "
                f"плановые часы — {expected}, "
                f"распределено по группам — {actual}."
            )

    @staticmethod
    def get_teacher_names(
        planned: PlannedWorkload,
    ) -> set[str]:
        distributions = getattr(
            planned,
            "report_approved_distributions",
            None,
        )

        if distributions is None:
            distributions = (
                planned.distributions
                .filter(
                    is_archived=False,
                    status=WorkloadDistribution.Status.APPROVED,
                    staff_employment__is_archived=False,
                    staff_employment__is_active=True,
                )
                .select_related(
                    "staff_employment",
                    "staff_employment__staff_member",
                )
            )

        return {
            distribution.teacher_name
            for distribution in distributions
            if distribution.teacher_name
        }

    @classmethod
    def add_workload_to_row(
        cls,
        *,
        row: dict,
        report_category: str,
        hours: Decimal,
        teacher_names: set[str],
    ) -> None:
        category = WorkloadType.ReportCategory

        if report_category == category.LECTURE:
            row["lecture_hours"] += hours
            row["teachers"]["lecture"].update(
                teacher_names
            )
            return

        if report_category == category.PRACTICE:
            row["practice_hours"] += hours
            row["teachers"]["practice"].update(
                teacher_names
            )
            return

        if report_category == category.LABORATORY:
            row["laboratory_hours"] += hours
            row["teachers"]["laboratory"].update(
                teacher_names
            )
            return

        if report_category == category.RATING:
            row["rating_hours"] += hours
            return

        if (
            report_category
            == category.COURSE_WORK_SUPERVISION
        ):
            row["course_work_supervision_hours"] += hours
            return

        if (
            report_category
            == category.COURSE_PROJECT_SUPERVISION
        ):
            row["course_project_supervision_hours"] += hours
            return

        if (
            report_category
            == category.COURSE_WORK_PROJECT_DEFENSE
        ):
            row["course_work_project_defense_hours"] += hours
            return

        if report_category in {
            category.SCIENTIFIC_PRACTICE,
            category.QUALIFICATION_PRACTICE,
        }:
            row["practice_supervision_hours"] += hours
            return

        if report_category in {
            category.GRADUATION_WORK_DEFENSE,
            category.MASTER_DISSERTATION_DEFENSE,
        }:
            row["graduation_defense_hours"] += hours
            return

        if report_category in {
            category.GRADUATION_WORK_SUPERVISION,
            category.MASTER_DISSERTATION_SUPERVISION,
        }:
            row["graduation_supervision_hours"] += hours
            return

        row["other_hours"] += hours

    @staticmethod
    def calculate_total_hours(row: dict) -> Decimal:
        return sum(
            (
                row["lecture_hours"],
                row["practice_hours"],
                row["laboratory_hours"],
                row["rating_hours"],
                row["course_work_supervision_hours"],
                row["course_project_supervision_hours"],
                row["course_work_project_defense_hours"],
                row["practice_supervision_hours"],
                row["graduation_defense_hours"],
                row["graduation_supervision_hours"],
                row["other_hours"],
            ),
            ZERO_HOURS,
        )

    @staticmethod
    def join_teacher_names(
        teacher_names: set[str],
    ) -> str:
        return ", ".join(sorted(teacher_names))

    @staticmethod
    def create_empty_row(
        *,
        planned: PlannedWorkload,
        group_semester,
    ) -> dict:
        curriculum_discipline = (
            planned.teaching_stream.curriculum_discipline
        )
        curriculum = curriculum_discipline.curriculum
        study_program = curriculum.study_program
        student_group = group_semester.student_group
        semester_number = group_semester.semester_number

        return {
            # A
            "faculty": student_group.faculty.name_ru,

            # B
            "study_form": student_group.study_form.name_ru,

            # C
            "study_program": (
                f"{study_program.code} — "
                f"{study_program.name_ru}"
            ),
            "study_program_code": study_program.code,

            # D
            "course": (semester_number + 1) // 2,

            # E
            "semester": semester_number,

            # F
            "discipline": (
                curriculum_discipline.discipline.name_ru
            ),

            # G
            "group": student_group.code,

            # H
            "students_count": (
                group_semester.students_count or 0
            ),

            # I, J
            "lecture_hours": ZERO_HOURS,
            "lecture_teacher": "",

            # K, L
            "practice_hours": ZERO_HOURS,
            "practice_teacher": "",

            # M, N
            "laboratory_hours": ZERO_HOURS,
            "laboratory_teacher": "",

            # O
            "rating_hours": ZERO_HOURS,

            # P
            "course_work_supervision_hours": ZERO_HOURS,

            # Q
            "course_project_supervision_hours": ZERO_HOURS,

            # R
            "course_work_project_defense_hours": ZERO_HOURS,

            # S
            "practice_supervision_hours": ZERO_HOURS,

            # T
            "graduation_defense_hours": ZERO_HOURS,

            # U
            "graduation_supervision_hours": ZERO_HOURS,

            # Не имеет отдельной колонки в шаблоне
            "other_hours": ZERO_HOURS,

            # V
            "total_hours": ZERO_HOURS,

            "teachers": defaultdict(set),
        }