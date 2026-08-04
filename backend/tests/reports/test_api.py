from io import BytesIO
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

from apps.access_control.models import (
    SystemRole,
)
from apps.reports.exceptions import (
    ReportDataError,
    ReportGenerationError,
)
from tests.assertions import (
    ApiResponseAssertionsMixin,
)
from tests.base import BaseAPITestCase
from tests.factories import (
    AcademicYearFactory,
    DepartmentFactory,
    StaffEmploymentFactory,
    StaffMemberFactory,
    StaffPositionFactory,
    UserFactory,
    UserRoleAssignmentFactory,
)


XLSX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument."
    "spreadsheetml.sheet"
)


class ReportsApiBase(
    ApiResponseAssertionsMixin,
    BaseAPITestCase,
):
    def setUp(self):
        self.user = self.create_global_admin()

        self.authenticate_with_jwt(
            user=self.user
        )


class ReportsAuthenticationApiTests(
    ReportsApiBase
):
    def test_teacher_report_requires_auth(
        self,
    ):
        self.logout_client()

        response = self.client.get(
            reverse(
                "reports:teacher-workload-excel"
            )
        )

        self.assert_authentication_required(
            response
        )

    def test_department_report_requires_auth(
        self,
    ):
        self.logout_client()

        response = self.client.get(
            reverse(
                (
                    "reports:"
                    "department-workload-excel"
                )
            )
        )

        self.assert_authentication_required(
            response
        )


class TeacherWorkloadReportApiTests(
    ReportsApiBase
):
    @patch(
        (
            "apps.reports.api.views."
            "TeacherWorkloadExcelService.build"
        ),
        return_value=BytesIO(b"xlsx-data"),
    )
    def test_global_admin_downloads_report(
        self,
        mocked_build,
    ):
        employment = StaffEmploymentFactory(
            position=StaffPositionFactory(
                is_teaching_position=True,
            ),
        )
        year = AcademicYearFactory()

        response = self.client.get(
            reverse(
                "reports:teacher-workload-excel"
            ),
            {
                "staff_employment": (
                    employment.pk
                ),
                "academic_year": year.pk,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response["Content-Type"],
            XLSX_CONTENT_TYPE,
        )
        self.assertIn(
            "attachment;",
            response[
                "Content-Disposition"
            ],
        )
        self.assertIn(
            ".xlsx",
            response[
                "Content-Disposition"
            ],
        )

        mocked_build.assert_called_once_with(
            staff_employment_id=employment.pk,
            academic_year=year,
        )

    def test_missing_parameters_rejected(self):
        response = self.client.get(
            reverse(
                "reports:teacher-workload-excel"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    @patch(
        (
            "apps.reports.api.views."
            "TeacherWorkloadExcelService.build"
        ),
        return_value=BytesIO(b"xlsx-data"),
    )
    def test_teacher_downloads_own_report(
        self,
        mocked_build,
    ):
        teacher_user = UserFactory()

        staff_member = StaffMemberFactory(
            user=teacher_user,
        )

        employment = StaffEmploymentFactory(
            staff_member=staff_member,
            position=StaffPositionFactory(
                is_teaching_position=True,
            ),
        )

        UserRoleAssignmentFactory.self_role(
            user=teacher_user,
            staff_member=staff_member,
            role_code=SystemRole.Code.TEACHER,
        )

        self.authenticate_with_jwt(
            user=teacher_user
        )

        response = self.client.get(
            reverse(
                "reports:teacher-workload-excel"
            ),
            {
                "staff_employment": (
                    employment.pk
                ),
                "academic_year": (
                    AcademicYearFactory().pk
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    @patch(
        (
            "apps.reports.api.views."
            "TeacherWorkloadExcelService.build"
        ),
        return_value=BytesIO(b"xlsx-data"),
    )
    def test_teacher_cannot_download_other_report(
        self,
        mocked_build,
    ):
        teacher_user = UserFactory()

        staff_member = StaffMemberFactory(
            user=teacher_user,
        )

        UserRoleAssignmentFactory.self_role(
            user=teacher_user,
            staff_member=staff_member,
            role_code=SystemRole.Code.TEACHER,
        )

        other_employment = (
            StaffEmploymentFactory(
                position=StaffPositionFactory(
                    is_teaching_position=True,
                ),
            )
        )

        self.authenticate_with_jwt(
            user=teacher_user
        )

        response = self.client.get(
            reverse(
                "reports:teacher-workload-excel"
            ),
            {
                "staff_employment": (
                    other_employment.pk
                ),
                "academic_year": (
                    AcademicYearFactory().pk
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        mocked_build.assert_not_called()

    @patch(
        (
            "apps.reports.api.views."
            "TeacherWorkloadExcelService.build"
        ),
        side_effect=ReportDataError(
            "Нет данных для отчёта."
        ),
    )
    def test_data_error_becomes_400(
        self,
        mocked_build,
    ):
        employment = StaffEmploymentFactory(
            position=StaffPositionFactory(
                is_teaching_position=True,
            ),
        )

        response = self.client.get(
            reverse(
                "reports:teacher-workload-excel"
            ),
            {
                "staff_employment": (
                    employment.pk
                ),
                "academic_year": (
                    AcademicYearFactory().pk
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(
            response.data["success"]
        )
        self.assertEqual(
            response.data["status_code"],
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["error"]["code"],
            "validation_error",
        )
        self.assertEqual(
            response.data["error"]["message"],
            "Нет данных для отчёта.",
        )

        fields = response.data["error"]["fields"]

        self.assertIn(
            "report",
            fields,
        )
        self.assertEqual(
            fields["report"]["message"],
            "Нет данных для отчёта.",
        )
        self.assertEqual(
            fields["report"]["code"],
            "invalid",
        )

    @patch(
        (
            "apps.reports.api.views."
            "TeacherWorkloadExcelService.build"
        ),
        side_effect=ReportGenerationError(
            "Шаблон повреждён."
        ),
    )
    def test_generation_error_becomes_400(
        self,
        mocked_build,
    ):
        employment = StaffEmploymentFactory(
            position=StaffPositionFactory(
                is_teaching_position=True,
            ),
        )

        response = self.client.get(
            reverse(
                "reports:teacher-workload-excel"
            ),
            {
                "staff_employment": (
                    employment.pk
                ),
                "academic_year": (
                    AcademicYearFactory().pk
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(
            response.data["success"]
        )
        self.assertEqual(
            response.data["status_code"],
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["error"]["code"],
            "validation_error",
        )
        self.assertEqual(
            response.data["error"]["message"],
            "Шаблон повреждён.",
        )

        fields = response.data["error"]["fields"]

        self.assertIn(
            "report",
            fields,
        )
        self.assertEqual(
            fields["report"]["message"],
            "Шаблон повреждён.",
        )
        self.assertEqual(
            fields["report"]["code"],
            "invalid",
        )


class DepartmentWorkloadReportApiTests(
    ReportsApiBase
):
    @patch(
        (
            "apps.reports.api.views."
            "DepartmentWorkloadExcelService.build"
        ),
        return_value=BytesIO(b"xlsx-data"),
    )
    def test_global_admin_downloads_report(
        self,
        mocked_build,
    ):
        department = DepartmentFactory()
        year = AcademicYearFactory()

        response = self.client.get(
            reverse(
                (
                    "reports:"
                    "department-workload-excel"
                )
            ),
            {
                "department": department.pk,
                "academic_year": year.pk,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response["Content-Type"],
            XLSX_CONTENT_TYPE,
        )
        self.assertIn(
            ".xlsx",
            response[
                "Content-Disposition"
            ],
        )

        mocked_build.assert_called_once_with(
            department_id=department.pk,
            academic_year=year,
        )

    @patch(
        (
            "apps.reports.api.views."
            "DepartmentWorkloadExcelService.build"
        ),
        return_value=BytesIO(b"xlsx-data"),
    )
    def test_department_head_downloads_own_report(
        self,
        mocked_build,
    ):
        department = DepartmentFactory()
        head_user = UserFactory()

        UserRoleAssignmentFactory.department_role(
            user=head_user,
            department=department,
            role_code=(
                SystemRole
                .Code
                .DEPARTMENT_HEAD
            ),
        )

        self.authenticate_with_jwt(
            user=head_user
        )

        response = self.client.get(
            reverse(
                (
                    "reports:"
                    "department-workload-excel"
                )
            ),
            {
                "department": department.pk,
                "academic_year": (
                    AcademicYearFactory().pk
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    @patch(
        (
            "apps.reports.api.views."
            "DepartmentWorkloadExcelService.build"
        ),
        return_value=BytesIO(b"xlsx-data"),
    )
    def test_department_head_cannot_download_other(
        self,
        mocked_build,
    ):
        own_department = DepartmentFactory()
        other_department = DepartmentFactory()
        head_user = UserFactory()

        UserRoleAssignmentFactory.department_role(
            user=head_user,
            department=own_department,
            role_code=(
                SystemRole
                .Code
                .DEPARTMENT_HEAD
            ),
        )

        self.authenticate_with_jwt(
            user=head_user
        )

        response = self.client.get(
            reverse(
                (
                    "reports:"
                    "department-workload-excel"
                )
            ),
            {
                "department": (
                    other_department.pk
                ),
                "academic_year": (
                    AcademicYearFactory().pk
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        mocked_build.assert_not_called()

    def test_missing_parameters_rejected(self):
        response = self.client.get(
            reverse(
                (
                    "reports:"
                    "department-workload-excel"
                )
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )