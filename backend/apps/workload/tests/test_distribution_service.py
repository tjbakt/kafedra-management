from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.academics.models import AcademicSemester, AcademicYear
from apps.curriculum.models import (
    Curriculum,
    CurriculumDiscipline,
    CurriculumWorkload,
    Discipline,
    WorkloadType,
)
from apps.staff.models import StaffEmploymentAcademicYear
from apps.staff.tests.factories import (
    create_department,
    create_employment,
    create_user,
)
from apps.teaching.models import PlannedWorkload, TeachingStream
from apps.workload.models import WorkloadDistribution
from apps.workload.services.distribution_service import (
    WorkloadDistributionService,
)


class WorkloadDistributionServiceTests(TestCase):
    def setUp(self):
        self.user = create_user(username="workload-user")

        self.academic_year = AcademicYear.objects.create(
            start_year=2026,
            end_year=2027,
            is_active=True,
        )

        self.academic_semester = AcademicSemester.objects.create(
            academic_year=self.academic_year,
            season=AcademicSemester.Season.AUTUMN,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 31),
            is_active=True,
        )

        self.department = create_department()

        self.employment = create_employment(
            department=self.department,
            rate=Decimal("1.00"),
        )
        self.second_employment = create_employment(
            department=self.department,
            rate=Decimal("1.00"),
            staff_member=None,  # создаст нового сотрудника
        )
        # если create_employment не принимает staff_member=None как «создать нового»,
        # оставь просто create_employment(department=self.department)

        # --- минимальная цепочка для PlannedWorkload ---
        workload_type = WorkloadType.objects.create(
            code=WorkloadType.Code.LECTURE,
            name_ru="Лекции",
            name_uz="Ma'ruzalar",
            calculation_mode=WorkloadType.CalculationMode.FIXED,
            is_active=True,
        )

        discipline = Discipline.objects.create(
            code="TEST-DISC",
            name_ru="Тестовая дисциплина",
            name_uz="Test fan",
            is_active=True,
        )

        # Curriculum и связанные объекты могут требовать study_program / study_form.
        # Если create падает — смотри обязательные поля в models и добавь их.
        from apps.academics.models import EducationLevel, StudyForm, StudyProgram
        from apps.organizations.models import University, Faculty

        university = self.department.faculty.university
        education_level = EducationLevel.objects.create(
            code=EducationLevel.Code.BACHELOR,
            name_ru="Бакалавриат",
            name_uz="Bakalavr",
            is_active=True,
        )
        study_form = StudyForm.objects.create(
            code=StudyForm.Code.FULL_TIME,
            name_ru="Очная",
            name_uz="Kunduzgi",
            is_active=True,
        )
        study_program = StudyProgram.objects.create(
            university=university,
            education_level=education_level,
            code="TEST-SP",
            name_ru="Тестовое направление",
            name_uz="Test yo'nalish",
            profiling_department=self.department,
            is_active=True,
        )

        curriculum = Curriculum.objects.create(
            study_program=study_program,
            study_form=study_form,
            code="CURR-TEST",
            name_ru="Тестовый УП",
            name_uz="Test UP",
            is_active=True,
        )

        curriculum_discipline = CurriculumDiscipline.objects.create(
            curriculum=curriculum,
            discipline=discipline,
            semester_number=1,
            is_active=True,
        )

        curriculum_workload = CurriculumWorkload.objects.create(
            curriculum_discipline=curriculum_discipline,
            workload_type=workload_type,
            calculation_mode=WorkloadType.CalculationMode.FIXED,
            base_hours=Decimal("100.00"),
        )

        teaching_stream = TeachingStream.objects.create(
            academic_year=self.academic_year,
            academic_semester=self.academic_semester,
            curriculum_discipline=curriculum_discipline,
            curriculum_workload=curriculum_workload,
            teaching_department=self.department,
            code="STREAM-1",
            name="Тестовый поток",
            is_active=True,
        )

        self.planned_workload = PlannedWorkload.objects.create(
            teaching_stream=teaching_stream,
            academic_year=self.academic_year,
            academic_semester=self.academic_semester,
            teaching_department=self.department,
            curriculum_workload=curriculum_workload,
            calculation_mode=WorkloadType.CalculationMode.FIXED,
            base_hours=Decimal("100.00"),
            calculation_quantity=Decimal("1.00"),
            total_hours=Decimal("100.00"),
            groups_count=1,
            subgroups_count=1,
            students_count=25,
            status=PlannedWorkload.Status.CALCULATED,
        )

    def test_cannot_distribute_without_year_staff_record(
        self,
    ):
        with self.assertRaises(ValidationError):
            WorkloadDistributionService.create_distribution(
                planned_workload=self.planned_workload,
                staff_employment=self.employment,
                allocated_hours=Decimal("20.00"),
                user=self.user,
            )

    def test_distribution_created_with_year_record(
        self,
    ):
        StaffEmploymentAcademicYear.objects.create(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            created_by=self.user,
            updated_by=self.user,
        )

        distribution = (
            WorkloadDistributionService
            .create_distribution(
                planned_workload=self.planned_workload,
                staff_employment=self.employment,
                allocated_hours=Decimal("20.00"),
                user=self.user,
            )
        )

        self.assertEqual(
            distribution.status,
            WorkloadDistribution.Status.DRAFT,
        )
        self.assertEqual(
            distribution.allocated_hours,
            Decimal("20.00"),
        )

    def test_cannot_exceed_remaining_hours(self):
        StaffEmploymentAcademicYear.objects.create(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            created_by=self.user,
            updated_by=self.user,
        )

        WorkloadDistributionService.create_distribution(
            planned_workload=self.planned_workload,
            staff_employment=self.employment,
            allocated_hours=Decimal("80.00"),
            user=self.user,
        )

        with self.assertRaises(ValidationError):
            WorkloadDistributionService.create_distribution(
                planned_workload=self.planned_workload,
                staff_employment=self.second_employment,
                allocated_hours=Decimal("30.00"),
                user=self.user,
            )

    def test_approve_sets_correct_status(self):
        StaffEmploymentAcademicYear.objects.create(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            created_by=self.user,
            updated_by=self.user,
        )

        distribution = (
            WorkloadDistributionService
            .create_distribution(
                planned_workload=self.planned_workload,
                staff_employment=self.employment,
                allocated_hours=Decimal("20.00"),
                user=self.user,
            )
        )

        distribution = (
            WorkloadDistributionService
            .approve_distribution(
                distribution=distribution,
                user=self.user,
            )
        )

        self.assertEqual(
            distribution.status,
            WorkloadDistribution.Status.APPROVED,
        )
        self.assertIsNotNone(
            distribution.approved_at
        )
        self.assertEqual(
            distribution.approved_by,
            self.user,
        )

    def test_approved_distribution_cannot_be_updated(
        self,
    ):
        StaffEmploymentAcademicYear.objects.create(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            created_by=self.user,
            updated_by=self.user,
        )

        distribution = (
            WorkloadDistributionService
            .create_distribution(
                planned_workload=self.planned_workload,
                staff_employment=self.employment,
                allocated_hours=Decimal("20.00"),
                user=self.user,
            )
        )

        distribution = (
            WorkloadDistributionService
            .approve_distribution(
                distribution=distribution,
                user=self.user,
            )
        )

        with self.assertRaises(ValidationError):
            WorkloadDistributionService.update_distribution(
                distribution=distribution,
                allocated_hours=Decimal("25.00"),
                user=self.user,
            )

    def test_cancel_releases_planned_hours(self):
        StaffEmploymentAcademicYear.objects.create(
            staff_employment=self.employment,
            academic_year=self.academic_year,
            rate=Decimal("1.00"),
            created_by=self.user,
            updated_by=self.user,
        )

        distribution = (
            WorkloadDistributionService
            .create_distribution(
                planned_workload=self.planned_workload,
                staff_employment=self.employment,
                allocated_hours=Decimal("20.00"),
                user=self.user,
            )
        )

        WorkloadDistributionService.cancel_distribution(
            distribution=distribution,
            user=self.user,
            reason="Перераспределение",
        )

        remaining = (
            WorkloadDistributionService
            .get_remaining_hours(
                self.planned_workload
            )
        )

        self.assertEqual(
            remaining,
            self.planned_workload.total_hours,
        )