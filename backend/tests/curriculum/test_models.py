from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.curriculum.models import (
    Curriculum,
    CurriculumDiscipline,
    WorkloadType,
)
from tests.factories import (
    CurriculumDisciplineFactory,
    CurriculumFactory,
    CurriculumWorkloadFactory,
    DepartmentFactory,
    DisciplineFactory,
    EducationDurationFactory,
    StudyFormFactory,
    WorkloadTypeFactory,
)
from apps.academics.models import (
    EducationDuration,
)


class DisciplineModelTests(TestCase):
    def test_string_representation(self):
        discipline = DisciplineFactory(
            code="MATH-01",
            name_ru="Высшая математика",
        )

        self.assertEqual(
            str(discipline),
            "MATH-01 — Высшая математика",
        )


class WorkloadTypeModelTests(TestCase):
    def test_string_representation(self):
        workload_type = WorkloadTypeFactory(
            name_ru="Лекции",
        )

        self.assertEqual(
            str(workload_type),
            "Лекции",
        )

    def test_all_codes_are_available(self):
        expected = {
            "lecture",
            "practice",
            "laboratory",
            "seminar",
            "consultation",
            "exam",
            "credit",
            "course_work",
            "course_project",
            "independent_work",
            "other",
        }

        actual = {
            value
            for value, _label
            in WorkloadType.Code.choices
        }

        self.assertEqual(
            actual,
            expected,
        )


class CurriculumModelTests(TestCase):
    def test_string_representation(self):
        curriculum = CurriculumFactory(
            code="CURR-TEST",
        )

        self.assertIn(
            "CURR-TEST",
            str(curriculum),
        )
        self.assertIn(
            curriculum.study_program.code,
            str(curriculum),
        )

    def test_approved_requires_date(self):
        curriculum = CurriculumFactory.build(
            status=Curriculum.Status.APPROVED,
            approved_at=None,
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            curriculum.full_clean()

        self.assertIn(
            "approved_at",
            context.exception.message_dict,
        )

    def test_duration_is_required(self):
        curriculum = CurriculumFactory()

        duration = EducationDuration.objects.get(
            education_level=(
                curriculum
                .study_program
                .education_level
            ),
            study_form=curriculum.study_form,
            is_archived=False,
        )

        duration.delete()

        with self.assertRaises(
                ValidationError
        ) as context:
            curriculum.full_clean()

        self.assertIn(
            "study_form",
            context.exception.message_dict,
        )

    def test_semesters_count_from_duration(self):
        curriculum = CurriculumFactory()

        duration = EducationDuration.objects.get(
            education_level=(
                curriculum
                .study_program
                .education_level
            ),
            study_form=curriculum.study_form,
            is_archived=False,
        )

        self.assertEqual(
            curriculum.semesters_count,
            duration.semesters_count,
        )


class CurriculumDisciplineModelTests(
    TestCase
):
    def test_string_representation(self):
        item = CurriculumDisciplineFactory(
            semester_number=3,
        )

        self.assertIn(
            item.curriculum.code,
            str(item),
        )
        self.assertIn(
            "3 семестр",
            str(item),
        )

    def test_odd_semester_is_autumn(self):
        item = CurriculumDisciplineFactory(
            semester_number=3,
        )

        self.assertEqual(
            item.season,
            "autumn",
        )

    def test_even_semester_is_spring(self):
        item = CurriculumDisciplineFactory(
            semester_number=4,
        )

        self.assertEqual(
            item.season,
            "spring",
        )

    def test_semester_cannot_exceed_duration(
        self,
    ):
        curriculum = CurriculumFactory()

        item = CurriculumDisciplineFactory.build(
            curriculum=curriculum,
            semester_number=9,
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            item.full_clean()

        self.assertIn(
            "semester_number",
            context.exception.message_dict,
        )

    def test_department_must_be_same_university(
        self,
    ):
        curriculum = CurriculumFactory()

        item = CurriculumDisciplineFactory.build(
            curriculum=curriculum,
            teaching_department=(
                DepartmentFactory()
            ),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            item.full_clean()

        self.assertIn(
            "teaching_department",
            context.exception.message_dict,
        )

    def test_independent_hours_cannot_exceed_total(
        self,
    ):
        item = CurriculumDisciplineFactory.build(
            total_academic_hours=Decimal("100.00"),
            independent_hours=Decimal("101.00"),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            item.full_clean()

        self.assertIn(
            "independent_hours",
            context.exception.message_dict,
        )

    def test_planned_contact_hours(self):
        item = CurriculumDisciplineFactory()

        CurriculumWorkloadFactory(
            curriculum_discipline=item,
            workload_type=WorkloadTypeFactory(
                code=WorkloadType.Code.LECTURE,
            ),
            base_hours=Decimal("30.00"),
        )
        CurriculumWorkloadFactory(
            curriculum_discipline=item,
            workload_type=WorkloadTypeFactory(
                code=WorkloadType.Code.PRACTICE,
                name_ru="Практические занятия",
                name_uz="Amaliy mashg‘ulot",
            ),
            base_hours=Decimal("20.00"),
        )

        self.assertEqual(
            item.planned_contact_hours,
            Decimal("50.00"),
        )


class CurriculumWorkloadModelTests(
    TestCase
):
    def test_fixed_hours(self):
        workload = CurriculumWorkloadFactory(
            calculation_mode=(
                WorkloadType
                .CalculationMode
                .FIXED
            ),
            base_hours=Decimal("24.00"),
        )

        self.assertEqual(
            workload.calculate_hours(
                groups_count=4,
                subgroups_count=8,
                students_count=100,
            ),
            Decimal("24.00"),
        )

    def test_per_group_hours(self):
        workload = CurriculumWorkloadFactory(
            calculation_mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),
            base_hours=Decimal("12.00"),
        )

        self.assertEqual(
            workload.calculate_hours(
                groups_count=3
            ),
            Decimal("36.00"),
        )

    def test_per_subgroup_hours(self):
        workload = CurriculumWorkloadFactory(
            calculation_mode=(
                WorkloadType
                .CalculationMode
                .PER_SUBGROUP
            ),
            base_hours=Decimal("10.00"),
        )

        self.assertEqual(
            workload.calculate_hours(
                subgroups_count=4
            ),
            Decimal("40.00"),
        )

    def test_per_student_hours(self):
        workload = CurriculumWorkloadFactory(
            calculation_mode=(
                WorkloadType
                .CalculationMode
                .PER_STUDENT
            ),
            base_hours=Decimal("0.50"),
        )

        self.assertEqual(
            workload.calculate_hours(
                students_count=20
            ),
            Decimal("10.00"),
        )

    def test_per_student_requires_positive_hours(
        self,
    ):
        workload = CurriculumWorkloadFactory.build(
            calculation_mode=(
                WorkloadType
                .CalculationMode
                .PER_STUDENT
            ),
            base_hours=Decimal("0.00"),
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            workload.full_clean()

        self.assertIn(
            "base_hours",
            context.exception.message_dict,
        )