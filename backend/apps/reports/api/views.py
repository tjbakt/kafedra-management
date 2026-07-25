from __future__ import annotations

from urllib.parse import quote

from django.http import FileResponse
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.access_control.models import SystemRole
from apps.access_control.services.access_service import (
    AccessService,
)
from apps.reports.api.serializers import (
    DepartmentWorkloadReportRequestSerializer,
    TeacherWorkloadReportRequestSerializer,
)
from apps.reports.exceptions import (
    ReportDataError,
    ReportGenerationError,
)
from apps.reports.services.department_workload_excel import (
    DepartmentWorkloadExcelService,
)
from apps.reports.services.teacher_workload_excel import (
    TeacherWorkloadExcelService,
)


EXCEL_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument."
    "spreadsheetml.sheet"
)


class BaseExcelReportView(APIView):
    """
    Базовое API-представление Excel-отчётов.
    """

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def create_excel_response(
        *,
        file_object,
        filename: str,
    ) -> FileResponse:
        response = FileResponse(
            file_object,
            as_attachment=True,
            content_type=EXCEL_CONTENT_TYPE,
        )

        response["Content-Disposition"] = (
            "attachment; "
            f"filename*=UTF-8''{quote(filename)}"
        )

        return response

    @staticmethod
    def sanitize_filename(value: str) -> str:
        """
        Удаляет символы, которые могут повредить имя файла.
        """

        result = str(value)

        for character in (
            "/",
            "\\",
            ":",
            "*",
            "?",
            '"',
            "<",
            ">",
            "|",
        ):
            result = result.replace(
                character,
                "_",
            )

        return result.strip()

    @staticmethod
    def raise_report_api_error(
        error: Exception,
    ) -> None:
        """
        Преобразует ошибки сервисного слоя
        в корректную ошибку DRF.
        """

        if isinstance(error, ReportDataError):
            raise ValidationError(
                {
                    "report": str(error),
                }
            ) from error

        if isinstance(error, ReportGenerationError):
            raise ValidationError(
                {
                    "report": (
                        str(error)
                        or "Не удалось сформировать отчёт."
                    ),
                }
            ) from error

        raise error


class TeacherWorkloadExcelView(
    BaseExcelReportView
):
    """
    Выгрузка годовой нагрузки преподавателя.
    """

    def get(self, request):
        serializer = (
            TeacherWorkloadReportRequestSerializer(
                data=request.query_params,
            )
        )
        serializer.is_valid(
            raise_exception=True
        )

        employment = serializer.validated_data[
            "staff_employment"
        ]
        academic_year = serializer.validated_data[
            "academic_year"
        ]

        can_view = (
            request.user.is_superuser
            or AccessService.has_global_role(
                request.user,
                SystemRole.Code.SYSTEM_ADMIN,
                SystemRole.Code.ACADEMIC_OFFICE,
            )
            or AccessService.can_manage_department(
                request.user,
                employment.department_id,
            )
            or AccessService.is_own_staff_member(
                request.user,
                employment.staff_member_id,
            )
        )

        if not can_view:
            raise PermissionDenied(
                "Нет доступа к нагрузке этого преподавателя."
            )

        try:
            file_object = (
                TeacherWorkloadExcelService.build(
                    staff_employment_id=employment.pk,
                    academic_year=academic_year,
                )
            )
        except (
            ReportDataError,
            ReportGenerationError,
        ) as exc:
            self.raise_report_api_error(exc)

        safe_name = self.sanitize_filename(
            employment.staff_member.full_name
        )
        safe_year = self.sanitize_filename(
            str(academic_year)
        )

        filename = (
            f"Нагрузка_{safe_name}_{safe_year}.xlsx"
        )

        return self.create_excel_response(
            file_object=file_object,
            filename=filename,
        )


class DepartmentWorkloadExcelView(
    BaseExcelReportView
):
    """
    Выгрузка общей нагрузки кафедры.
    """

    def get(self, request):
        serializer = (
            DepartmentWorkloadReportRequestSerializer(
                data=request.query_params,
            )
        )
        serializer.is_valid(
            raise_exception=True
        )

        department = serializer.validated_data[
            "department"
        ]
        academic_year = serializer.validated_data[
            "academic_year"
        ]

        can_view = (
            request.user.is_superuser
            or AccessService.has_global_role(
                request.user,
                SystemRole.Code.SYSTEM_ADMIN,
                SystemRole.Code.ACADEMIC_OFFICE,
            )
            or AccessService.can_manage_department(
                request.user,
                department.pk,
            )
        )

        if not can_view:
            raise PermissionDenied(
                "Нет доступа к нагрузке этой кафедры."
            )

        try:
            file_object = (
                DepartmentWorkloadExcelService.build(
                    department_id=department.pk,
                    academic_year=academic_year,
                )
            )
        except (
            ReportDataError,
            ReportGenerationError,
        ) as exc:
            self.raise_report_api_error(exc)

        safe_department = self.sanitize_filename(
            department.name_ru
        )
        safe_year = self.sanitize_filename(
            str(academic_year)
        )

        filename = (
            f"Нагрузка_кафедры_"
            f"{safe_department}_"
            f"{safe_year}.xlsx"
        )

        return self.create_excel_response(
            file_object=file_object,
            filename=filename,
        )