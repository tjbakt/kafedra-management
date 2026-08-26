from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.curriculum.api.serializers import (
    CurriculumDisciplineSerializer,
    CurriculumSerializer,
    CurriculumWorkloadSerializer,
    DisciplineSerializer,
    WorkloadTypeSerializer,
)
from apps.curriculum.models import (
    Curriculum,
    CurriculumDiscipline,
    WorkloadType,
)
from tests.factories import (
    AcademicYearFactory,
    CurriculumFactory,
    DepartmentFactory,
    DisciplineFactory,
    EducationDurationFactory,
    StudyFormFactory,
    StudyProgramFactory,
    WorkloadTypeFactory,
    CurriculumDisciplineFactory,
)


class DisciplineSerializerTests(TestCase):
    def test_code_is_normalized(self):
        serializer = DisciplineSerializer(
            data={
                "code": " math-01 ",
                "name_ru": "Математика",
                "name_uz": "Matematika",
                "is_active": True,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )
        self.assertEqual(
            serializer.validated_data["code"],
            "MATH-01",
        )

    def test_archive_fields_are_read_only(self):
        discipline = DisciplineFactory()

        serializer = DisciplineSerializer(
            discipline,
            data={
                "name_ru": "Новое название",
                "is_archived": True,
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        discipline = serializer.save()

        self.assertFalse(
            discipline.is_archived
        )


class WorkloadTypeSerializerTests(TestCase):
    def test_report_category_is_available(self):
        workload_type = WorkloadTypeFactory(
            report_category=(
                WorkloadType
                .ReportCategory
                .LECTURE
            ),
        )

        serializer = WorkloadTypeSerializer(
            workload_type
        )

        self.assertEqual(
            serializer.data["report_category"],
            WorkloadType.ReportCategory.LECTURE,
        )
        self.assertIn(
            "report_category_name",
            serializer.data,
        )


class CurriculumSerializerTests(TestCase):
    def test_code_is_normalized(self):
        program = StudyProgramFactory()
        study_form = StudyFormFactory()
        year = AcademicYearFactory()

        EducationDurationFactory(
            education_level=(
                program.education_level
            ),
            study_form=study_form,
        )

        serializer = CurriculumSerializer(
            data={
                "study_program": program.pk,
                "study_form": study_form.pk,
                "effective_academic_year": (
                    year.pk
                ),
                "code": " curr-test ",
                "version": 1,
                "status": Curriculum.Status.DRAFT,
                "is_active": True,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )
        self.assertEqual(
            serializer.validated_data["code"],
            "CURR-TEST",
        )

    def test_approved_requires_date(self):
        curriculum = CurriculumFactory()

        serializer = CurriculumSerializer(
            curriculum,
            data={
                "status": (
                    Curriculum.Status.APPROVED
                ),
                "approved_at": None,
            },
            partial=True,
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "approved_at",
            serializer.errors,
        )

    def test_unconfigured_duration_rejected(
        self,
    ):
        program = StudyProgramFactory()
        study_form = StudyFormFactory(
            code="distance",
            name_ru="Дистанционная",
            name_uz="Masofaviy",
        )

        serializer = CurriculumSerializer(
            data={
                "study_program": program.pk,
                "study_form": study_form.pk,
                "effective_academic_year": (
                    AcademicYearFactory().pk
                ),
                "code": "CURR-NO-DURATION",
                "version": 1,
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "study_form",
            serializer.errors,
        )


class CurriculumDisciplineSerializerTests(
    TestCase
):
    def test_rejects_excess_semester(self):
        curriculum = CurriculumFactory()

        discipline = DisciplineFactory(
            default_department=(
                curriculum
                .study_program
                .profiling_department
            )
        )
        serializer = (
            CurriculumDisciplineSerializer(
                data={
                    "curriculum": curriculum.pk,
                    "discipline": discipline.pk,
                    "semester_number": 9,
                    "component_type": (
                        CurriculumDiscipline
                        .ComponentType
                        .REQUIRED
                    ),
                    "control_form": (
                        CurriculumDiscipline
                        .ControlForm
                        .EXAM
                    ),
                    "credits": "6.00",
                    "total_academic_hours": (
                        "180.00"
                    ),
                    "independent_hours": (
                        "90.00"
                    ),
                    "weeks_count": 15,
                }
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "semester_number",
            serializer.errors,
        )

    def test_rejects_discipline_from_other_university(
            self,
    ):
        curriculum = (
            CurriculumFactory()
        )

        discipline = (
            DisciplineFactory(
                default_department=(
                    DepartmentFactory()
                )
            )
        )

        serializer = (
            CurriculumDisciplineSerializer(
                data={
                    "curriculum":
                        curriculum.pk,

                    "discipline":
                        discipline.pk,

                    "semester_number":
                        1,

                    "credits":
                        "6.00",

                    "total_academic_hours":
                        "180.00",

                    "independent_hours":
                        "90.00",

                    "weeks_count":
                        15,
                }
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "discipline",
            serializer.errors,
        )

    def test_rejects_excess_independent_hours(
            self,
    ):
        curriculum = (
            CurriculumFactory()
        )

        discipline = (
            DisciplineFactory(
                default_department=(
                    curriculum
                    .study_program
                    .profiling_department
                )
            )
        )

        serializer = (
            CurriculumDisciplineSerializer(
                data={
                    "curriculum":
                        curriculum.pk,

                    "discipline":
                        discipline.pk,

                    "semester_number":
                        1,

                    "credits":
                        "6.00",

                    "total_academic_hours":
                        "100.00",

                    "independent_hours":
                        "101.00",

                    "weeks_count":
                        15,
                }
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "independent_hours",
            serializer.errors,
        )


class CurriculumWorkloadSerializerTests(
    TestCase
):
    def test_default_calculation_mode(self):
        workload_type = WorkloadTypeFactory(
            calculation_mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),
        )

        serializer = CurriculumWorkloadSerializer(
            data={
                "curriculum_discipline": (
                    CurriculumDisciplineFactory().pk
                ),
                "workload_type": (
                    workload_type.pk
                ),
                "base_hours": "30.00",
                "is_active": True,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )
        self.assertEqual(
            serializer.validated_data[
                "calculation_mode"
            ],
            (
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),
        )

    def test_per_student_requires_positive_hours(
        self,
    ):
        workload_type = WorkloadTypeFactory(
            code=WorkloadType.Code.OTHER,
            name_ru="Другая нагрузка",
            name_uz="Boshqa yuklama",
            calculation_mode=(
                WorkloadType
                .CalculationMode
                .PER_STUDENT
            ),
        )

        from tests.factories import (
            CurriculumDisciplineFactory,
        )

        serializer = CurriculumWorkloadSerializer(
            data={
                "curriculum_discipline": (
                    CurriculumDisciplineFactory().pk
                ),
                "workload_type": (
                    workload_type.pk
                ),
                "calculation_mode": (
                    WorkloadType
                    .CalculationMode
                    .PER_STUDENT
                ),
                "base_hours": "0.00",
                "is_active": True,
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "base_hours",
            serializer.errors,
        )