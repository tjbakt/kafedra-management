from datetime import date
from decimal import Decimal

from django.urls import reverse
from rest_framework import status

from apps.curriculum.models import (
    Curriculum,
    CurriculumDiscipline,
    CurriculumWorkload,
    Discipline,
    WorkloadType,
)
from tests.assertions import (
    ApiResponseAssertionsMixin,
)
from tests.base import BaseAPITestCase
from tests.factories import (
    AcademicYearFactory,
    CurriculumDisciplineFactory,
    CurriculumFactory,
    CurriculumWorkloadFactory,
    DepartmentFactory,
    DisciplineFactory,
    EducationDurationFactory,
    StudyFormFactory,
    StudyProgramFactory,
    UserFactory,
    WorkloadTypeFactory,
)


class CurriculumApiBase(
    ApiResponseAssertionsMixin,
    BaseAPITestCase,
):
    def setUp(self):
        self.user = UserFactory()

        self.authenticate_with_jwt(
            user=self.user
        )

    def results(self, response):
        if isinstance(response.data, list):
            return response.data

        return response.data["results"]


class DisciplineApiTests(CurriculumApiBase):
    def setUp(self):
        super().setUp()
        self.list_url = reverse(
            "discipline-list"
        )

    def detail_url(self, instance):
        return reverse(
            "discipline-detail",
            kwargs={"pk": instance.pk},
        )

    def test_requires_authentication(self):
        self.logout_client()

        response = self.client.get(
            self.list_url
        )

        self.assert_authentication_required(
            response
        )

    def test_create_discipline(self):
        department = DepartmentFactory()

        response = self.client.post(
            self.list_url,
            {
                "code": " math-api ",
                "name_ru": "Математика",
                "name_uz": "Matematika",
                "default_department": (
                    department.pk
                ),
                "is_active": True,
                "sort_order": 0,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["code"],
            "MATH-API",
        )

        discipline = Discipline.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            discipline.created_by,
            self.user,
        )

    def test_filter_by_department(self):
        department = DepartmentFactory()

        expected = DisciplineFactory(
            default_department=department,
        )
        DisciplineFactory()

        response = self.client.get(
            self.list_url,
            {
                "default_department": (
                    department.pk
                )
            },
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertEqual(
            ids,
            {expected.pk},
        )

    def test_query_filter(self):
        expected = DisciplineFactory(
            code="UNIQUE-DISCIPLINE",
        )
        DisciplineFactory(
            code="OTHER-DISCIPLINE",
        )

        response = self.client.get(
            self.list_url,
            {
                "query": "unique",
            },
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertEqual(
            ids,
            {expected.pk},
        )

    def test_archive_and_restore(self):
        discipline = DisciplineFactory()

        delete_response = self.client.delete(
            self.detail_url(discipline)
        )

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_200_OK,
        )

        restore_response = self.client.post(
            reverse(
                "discipline-restore",
                kwargs={
                    "pk": discipline.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            restore_response.status_code,
            status.HTTP_200_OK,
        )

        discipline.refresh_from_db()

        self.assertFalse(
            discipline.is_archived
        )


class WorkloadTypeApiTests(
    CurriculumApiBase
):
    def setUp(self):
        super().setUp()
        self.list_url = reverse(
            "workload-type-list"
        )

    def test_create_workload_type(self):
        response = self.client.post(
            self.list_url,
            {
                "code": (
                    WorkloadType.Code.PRACTICE
                ),
                "name_ru": (
                    "Практические занятия"
                ),
                "name_uz": (
                    "Amaliy mashg‘ulot"
                ),
                "calculation_mode": (
                    WorkloadType
                    .CalculationMode
                    .PER_GROUP
                ),
                "report_category": (
                    WorkloadType
                    .ReportCategory
                    .PRACTICE
                ),
                "is_classroom": True,
                "is_teaching_load": True,
                "is_active": True,
                "sort_order": 20,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["report_category"],
            (
                WorkloadType
                .ReportCategory
                .PRACTICE
            ),
        )

    def test_filter_by_calculation_mode(
            self,
    ):
        expected = WorkloadTypeFactory(
            code=WorkloadType.Code.EXAM,
            name_ru="Экзамен",
            name_uz="Imtihon",
            calculation_mode=(
                WorkloadType
                .CalculationMode
                .PER_STUDENT
            ),
        )

        fixed = WorkloadTypeFactory(
            code=WorkloadType.Code.CREDIT,
            name_ru="Зачёт",
            name_uz="Sinov",
            calculation_mode=(
                WorkloadType
                .CalculationMode
                .FIXED
            ),
        )

        response = self.client.get(
            self.list_url,
            {
                "calculation_mode": (
                    WorkloadType
                    .CalculationMode
                    .PER_STUDENT
                )
            },
        )

        ids = {
            item["id"]
            for item
            in self.results(
                response
            )
        }

        self.assertIn(
            expected.pk,
            ids,
        )

        self.assertNotIn(
            fixed.pk,
            ids,
        )


class CurriculumApiTests(CurriculumApiBase):
    def setUp(self):
        super().setUp()
        self.list_url = reverse(
            "curriculum-list"
        )

    def detail_url(self, instance):
        return reverse(
            "curriculum-detail",
            kwargs={"pk": instance.pk},
        )

    def test_create_curriculum(self):
        program = StudyProgramFactory()
        study_form = StudyFormFactory()
        year = AcademicYearFactory()

        EducationDurationFactory(
            education_level=(
                program.education_level
            ),
            study_form=study_form,
        )

        response = self.client.post(
            self.list_url,
            {
                "study_program": program.pk,
                "study_form": study_form.pk,
                "effective_academic_year": (
                    year.pk
                ),
                "code": " curr-api ",
                "version": 1,
                "status": Curriculum.Status.DRAFT,
                "is_active": True,
                "notes": "",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["code"],
            "CURR-API",
        )

    def test_approved_requires_date(self):
        source = CurriculumFactory()

        response = self.client.patch(
            self.detail_url(source),
            {
                "status": (
                    Curriculum.Status.APPROVED
                ),
            },
            format="json",
        )

        self.assert_validation_error(
            response,
            field="approved_at",
        )

    def test_filter_by_university(self):
        expected = CurriculumFactory()
        CurriculumFactory()

        response = self.client.get(
            self.list_url,
            {
                "university": (
                    expected
                    .study_program
                    .university_id
                )
            },
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertEqual(
            ids,
            {expected.pk},
        )

    def test_disciplines_count(self):
        curriculum = CurriculumFactory()

        CurriculumDisciplineFactory.create_batch(
            2,
            curriculum=curriculum,
        )

        response = self.client.get(
            self.detail_url(curriculum)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["disciplines_count"],
            2,
        )

    def test_archive_and_restore(self):
        curriculum = CurriculumFactory()

        delete_response = self.client.delete(
            self.detail_url(curriculum)
        )

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_200_OK,
        )

        restore_response = self.client.post(
            reverse(
                "curriculum-restore",
                kwargs={
                    "pk": curriculum.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            restore_response.status_code,
            status.HTTP_200_OK,
        )


class CurriculumDisciplineApiTests(
    CurriculumApiBase
):
    def setUp(self):
        super().setUp()

        self.list_url = reverse(
            "curriculum-discipline-list"
        )

    def detail_url(self, instance):
        return reverse(
            "curriculum-discipline-detail",
            kwargs={"pk": instance.pk},
        )

    def test_create_curriculum_discipline(
        self,
    ):
        curriculum = CurriculumFactory()
        discipline = DisciplineFactory(
            default_department=(
                curriculum
                .study_program
                .profiling_department
            )
        )

        response = self.client.post(
            self.list_url,
            {
                "curriculum": curriculum.pk,
                "discipline": discipline.pk,
                "semester_number": 1,

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
                "independent_hours": "90.00",
                "weeks_count": 15,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["season"],
            "autumn",
        )

    def test_invalid_semester_rejected(self):
        curriculum = CurriculumFactory()

        response = self.client.post(
            self.list_url,
            {
                "curriculum": curriculum.pk,
                "discipline": (
                    DisciplineFactory(
                        default_department=(
                            curriculum
                            .study_program
                            .profiling_department
                        )
                    ).pk
                ),
                "semester_number": 9,
                "teaching_department": (
                    curriculum
                    .study_program
                    .profiling_department_id
                ),
                "credits": "6.00",
                "total_academic_hours": (
                    "180.00"
                ),
                "independent_hours": "90.00",
                "weeks_count": 15,
            },
            format="json",
        )

        self.assert_validation_error(
            response,
            field="semester_number",
        )

    def test_filter_by_season(self):
        curriculum = CurriculumFactory()

        autumn = CurriculumDisciplineFactory(
            curriculum=curriculum,
            semester_number=1,
        )
        spring = CurriculumDisciplineFactory(
            curriculum=curriculum,
            semester_number=2,
        )

        response = self.client.get(
            self.list_url,
            {
                "curriculum": curriculum.pk,
                "season": "autumn",
            },
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertIn(
            autumn.pk,
            ids,
        )
        self.assertNotIn(
            spring.pk,
            ids,
        )

    def test_nested_workload_items(self):
        item = CurriculumDisciplineFactory()

        workload = CurriculumWorkloadFactory(
            curriculum_discipline=item,
        )

        response = self.client.get(
            self.detail_url(item)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        workload_ids = {
            child["id"]
            for child
            in response.data["workload_items"]
        }

        self.assertIn(
            workload.pk,
            workload_ids,
        )


class CurriculumWorkloadApiTests(
    CurriculumApiBase
):
    def setUp(self):
        super().setUp()

        self.list_url = reverse(
            "curriculum-workload-list"
        )

    def test_create_workload_uses_default_mode(
        self,
    ):
        item = CurriculumDisciplineFactory()

        workload_type = WorkloadTypeFactory(
            calculation_mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),
        )

        response = self.client.post(
            self.list_url,
            {
                "curriculum_discipline": (
                    item.pk
                ),
                "workload_type": (
                    workload_type.pk
                ),
                "base_hours": "30.00",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["calculation_mode"],
            (
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),
        )

    def test_per_student_zero_hours_rejected(
        self,
    ):
        item = CurriculumDisciplineFactory()

        workload_type = WorkloadTypeFactory(
            code=WorkloadType.Code.OTHER,
            name_ru="Другая работа",
            name_uz="Boshqa ish",
            calculation_mode=(
                WorkloadType
                .CalculationMode
                .PER_STUDENT
            ),
        )

        response = self.client.post(
            self.list_url,
            {
                "curriculum_discipline": (
                    item.pk
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
            },
            format="json",
        )

        self.assert_validation_error(
            response,
            field="base_hours",
        )

    def test_filter_by_curriculum(self):
        expected = CurriculumWorkloadFactory()

        CurriculumWorkloadFactory(
            workload_type=WorkloadTypeFactory(
                code=WorkloadType.Code.PRACTICE,
                name_ru="Практические занятия",
                name_uz="Amaliy mashg‘ulot",
            ),
        )

        response = self.client.get(
            self.list_url,
            {
                "curriculum": (
                    expected
                    .curriculum_discipline
                    .curriculum_id
                )
            },
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertEqual(
            ids,
            {expected.pk},
        )