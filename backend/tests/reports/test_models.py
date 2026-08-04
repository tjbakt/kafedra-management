from django.core.exceptions import (
    ValidationError,
)
from django.core.files.uploadedfile import (
    SimpleUploadedFile,
)
from django.db import IntegrityError
from django.test import TestCase

from apps.reports.models import (
    ExcelReportTemplate,
    report_template_upload_to,
)
from tests.factories import (
    ExcelReportTemplateFactory,
    UniversityFactory,
)


class ExcelReportTemplateModelTests(
    TestCase
):
    def test_string_representation(self):
        template = (
            ExcelReportTemplateFactory(
                version=3,
            )
        )

        value = str(template)

        self.assertIn(
            template.get_template_type_display(),
            value,
        )
        self.assertIn(
            template.university.name_ru,
            value,
        )
        self.assertIn(
            "версия 3",
            value,
        )

    def test_global_string_representation(
        self,
    ):
        template = (
            ExcelReportTemplateFactory
            .global_template()
        )

        self.assertIn(
            "Общий шаблон",
            str(template),
        )

    def test_upload_path(self):
        template = (
            ExcelReportTemplateFactory.build(
                template_type=(
                    ExcelReportTemplate
                    .Type
                    .TEACHER_WORKLOAD
                )
            )
        )

        path = report_template_upload_to(
            template,
            "teacher.xlsx",
        )

        self.assertEqual(
            path,
            (
                "report_templates/"
                "teacher_workload/"
                "teacher.xlsx"
            ),
        )

    def test_rejects_non_xlsx_file(self):
        template = (
            ExcelReportTemplateFactory.build(
                file=SimpleUploadedFile(
                    "template.xls",
                    b"invalid",
                    content_type=(
                        "application/vnd.ms-excel"
                    ),
                )
            )
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            template.full_clean()

        self.assertIn(
            "file",
            context.exception.message_dict,
        )

    def test_accepts_xlsx_file(self):
        template = (
            ExcelReportTemplateFactory.build()
        )

        template.full_clean()

    def test_only_one_active_global_template(
        self,
    ):
        (
            ExcelReportTemplateFactory
            .global_template()
        )

        with self.assertRaises(
            IntegrityError
        ):
            (
                ExcelReportTemplateFactory
                .global_template()
            )

    def test_inactive_global_template_allowed(
        self,
    ):
        (
            ExcelReportTemplateFactory
            .global_template()
        )

        second = (
            ExcelReportTemplateFactory
            .global_template(
                is_active=False,
                version=2,
            )
        )

        self.assertIsNotNone(second.pk)

    def test_only_one_active_university_template(
        self,
    ):
        university = UniversityFactory()

        ExcelReportTemplateFactory(
            university=university,
        )

        with self.assertRaises(
            IntegrityError
        ):
            ExcelReportTemplateFactory(
                university=university,
                version=2,
            )

    def test_different_template_types_allowed(
        self,
    ):
        university = UniversityFactory()

        teacher = ExcelReportTemplateFactory(
            university=university,
            template_type=(
                ExcelReportTemplate
                .Type
                .TEACHER_WORKLOAD
            ),
        )

        department = (
            ExcelReportTemplateFactory
            .department_template(
                university=university,
            )
        )

        self.assertNotEqual(
            teacher.template_type,
            department.template_type,
        )