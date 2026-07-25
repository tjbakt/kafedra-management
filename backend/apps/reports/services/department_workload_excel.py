from decimal import Decimal

from apps.academics.models import AcademicYear
from apps.organizations.models import Department
from apps.reports.models import ExcelReportTemplate
from apps.reports.services.base_excel_report import (
    BaseExcelReportService,
)
from apps.reports.services.department_workload_report import (
    DepartmentWorkloadReportService,
)


class DepartmentWorkloadExcelService(
    BaseExcelReportService
):
    """
    Формирует отчёт:
    «Общая нагрузка кафедры за учебный год».
    """

    template_type = (
        ExcelReportTemplate.Type.DEPARTMENT_WORKLOAD
    )

    FIRST_DATA_ROW = 4
    MAX_COLUMN = 22  # V

    @classmethod
    def build(
        cls,
        *,
        department_id: int,
        academic_year: AcademicYear,
    ):
        department = (
            Department.objects
            .select_related(
                "faculty",
                "faculty__university",
            )
            .get(
                pk=department_id,
                is_archived=False,
            )
        )

        university_id = (
            department.faculty.university_id
        )

        template = cls.get_template(
            university_id=university_id,
        )

        workbook, worksheet = (
            cls.load_template_workbook(template)
        )

        cls.replace_placeholders(
            worksheet,
            {
                "{department}": department.name_ru,
                "{year}": str(academic_year),
            },
        )

        planned_workloads = (
            DepartmentWorkloadReportService
            .get_planned_workloads(
                department_id=department.pk,
                academic_year_id=academic_year.pk,
            )
        )

        rows = (
            DepartmentWorkloadReportService
            .prepare_rows(planned_workloads)
        )

        cls.fill_report(
            worksheet=worksheet,
            rows=rows,
        )

        return cls.save_to_bytes(workbook)

    @classmethod
    def fill_report(
        cls,
        *,
        worksheet,
        rows: list[dict],
    ) -> None:
        source_style_row = cls.FIRST_DATA_ROW

        if not rows:
            cls.clear_row_values(
                worksheet,
                row=source_style_row,
                min_column=1,
                max_column=cls.MAX_COLUMN,
            )
            return

        for index, item in enumerate(rows):
            target_row = cls.FIRST_DATA_ROW + index

            if index > 0:
                worksheet.insert_rows(target_row)

                cls.copy_row_style(
                    worksheet,
                    source_row=source_style_row,
                    target_row=target_row,
                    min_column=1,
                    max_column=cls.MAX_COLUMN,
                )

            cls.write_data_row(
                worksheet=worksheet,
                row=target_row,
                item=item,
            )

    @classmethod
    def write_data_row(
        cls,
        *,
        worksheet,
        row: int,
        item: dict,
    ) -> None:
        values = {
            1: item["faculty"],                         # A
            2: item["study_form"],                      # B
            3: item["study_program"],                   # C
            4: item["course"],                          # D
            5: item["semester"],                        # E
            6: item["discipline"],                      # F
            7: item["group"],                           # G
            8: item["students_count"],                  # H
            9: cls.hours_or_empty(
                item["lecture_hours"]
            ),                                          # I
            10: item["lecture_teacher"],                # J
            11: cls.hours_or_empty(
                item["practice_hours"]
            ),                                          # K
            12: item["practice_teacher"],               # L
            13: cls.hours_or_empty(
                item["laboratory_hours"]
            ),                                          # M
            14: item["laboratory_teacher"],             # N
            15: cls.hours_or_empty(
                item["rating_hours"]
            ),                                          # O
            16: cls.hours_or_empty(
                item["course_work_supervision_hours"]
            ),                                          # P
            17: cls.hours_or_empty(
                item["course_project_supervision_hours"]
            ),                                          # Q
            18: cls.hours_or_empty(
                item["course_work_project_defense_hours"]
            ),                                          # R
            19: cls.hours_or_empty(
                item["practice_supervision_hours"]
            ),                                          # S
            20: cls.hours_or_empty(
                item["graduation_defense_hours"]
            ),                                          # T
            21: cls.hours_or_empty(
                item["graduation_supervision_hours"]
            ),                                          # U
            22: float(item["total_hours"]),             # V
        }

        for column, value in values.items():
            worksheet.cell(
                row=row,
                column=column,
            ).value = value

    @staticmethod
    def hours_or_empty(value):
        value = Decimal(value or Decimal("0.00"))

        if value == Decimal("0.00"):
            return None

        return float(value)