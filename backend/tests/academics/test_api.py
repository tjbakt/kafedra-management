from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

from apps.access_control.models import (
    SystemRole,
)
from apps.academics.models import (
    AcademicYear,
    EducationDuration,
)
from tests.assertions import (
    ApiResponseAssertionsMixin,
)
from tests.base import BaseAPITestCase
from tests.factories import (
    AcademicSemesterFactory,
    AcademicYearFactory,
    DepartmentFactory,
    EducationDurationFactory,
    EducationLevelFactory,
    FacultyFactory,
    StudentGroupFactory,
    StudyFormFactory,
    StudyProgramFactory,
    UniversityFactory,
    UserFactory,
    UserRoleAssignmentFactory,
)
from django.utils import timezone


class AcademicsApiBase(
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


class AcademicYearApiTests(
    AcademicsApiBase
):
    def setUp(self):
        super().setUp()

        self.list_url = reverse(
            "academic-year-list"
        )

    def detail_url(self, academic_year):
        return reverse(
            "academic-year-detail",
            kwargs={
                "pk": academic_year.pk,
            },
        )

    def test_requires_authentication(self):
        self.logout_client()

        response = self.client.get(
            self.list_url
        )

        self.assert_authentication_required(
            response
        )

    def test_authenticated_user_can_create(self):
        response = self.client.post(
            self.list_url,
            {
                "start_year": 2035,
                "end_year": 2036,
                "is_current": False,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        academic_year = AcademicYear.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            academic_year.created_by,
            self.user,
        )

    def test_invalid_range_rejected(self):
        response = self.client.post(
            self.list_url,
            {
                "start_year": 2035,
                "end_year": 2037,
            },
            format="json",
        )

        self.assert_validation_error(
            response,
            field="end_year",
        )

    def test_filter_by_status(self):
        opened = AcademicYearFactory()
        AcademicYearFactory.closed()

        response = self.client.get(
            self.list_url,
            {
                "status": (
                    AcademicYear.Status.OPEN
                )
            },
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertIn(
            opened.pk,
            ids,
        )

    def test_archive_and_restore(self):
        academic_year = (
            AcademicYearFactory()
        )

        delete_response = self.client.delete(
            self.detail_url(academic_year)
        )

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_200_OK,
        )

        restore_response = self.client.post(
            reverse(
                "academic-year-restore",
                kwargs={
                    "pk": academic_year.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            restore_response.status_code,
            status.HTTP_200_OK,
        )

        academic_year.refresh_from_db()

        self.assertFalse(
            academic_year.is_archived
        )

    def test_regular_user_cannot_close_year(
        self,
    ):
        academic_year = (
            AcademicYearFactory()
        )

        response = self.client.post(
            reverse(
                "academic-year-close",
                kwargs={
                    "pk": academic_year.pk,
                },
            ),
            {
                "comment": "Закрытие",
            },
            format="json",
        )

        self.assert_permission_denied(
            response
        )

    @patch(
        (
            "apps.academics.api.views."
            "AcademicYearClosingService.close"
        )
    )
    def test_academic_office_can_close_year(
        self,
        mocked_close,
    ):
        academic_user = UserFactory()

        UserRoleAssignmentFactory.global_role(
            user=academic_user,
            role_code=(
                SystemRole.Code.ACADEMIC_OFFICE
            ),
        )

        academic_year = AcademicYearFactory(
            start_year=2040,
            end_year=2041,
        )

        readiness = {
            "academic_year": academic_year.pk,
            "academic_year_name": (
                academic_year.name
            ),
            "department_ids": [],
            "ready_to_close": True,
            "status": "ready",
            "message": "Готов.",
            "summary": {
                "planned_workloads_count": 0,
                "distributions_count": 0,
                "year_staff_records_count": 0,
                "blocking_issues_count": 0,
                "warnings_count": 0,
                "blocking_issues_by_type": {},
                "warnings_by_type": {},
            },
            "blocking_issues": [],
            "warnings": [],
        }

        def close_side_effect(**kwargs):
            year = kwargs["academic_year"]
            year.status = (
                AcademicYear.Status.CLOSED
            )
            year.is_active = False
            year.is_current = False
            year.closed_by = kwargs["user"]
            year.closed_at = timezone.now()
            year.closing_comment = (
                kwargs["comment"]
            )
            year.save()

            return year, readiness

        mocked_close.side_effect = (
            close_side_effect
        )

        self.authenticate_with_jwt(
            user=academic_user
        )

        response = self.client.post(
            reverse(
                "academic-year-close",
                kwargs={
                    "pk": academic_year.pk,
                },
            ),
            {
                "comment": "Год завершён",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["status"],
            AcademicYear.Status.CLOSED,
        )

    def test_reopen_requires_reason(self):
        academic_user = UserFactory()

        UserRoleAssignmentFactory.global_role(
            user=academic_user,
            role_code=(
                SystemRole.Code.ACADEMIC_OFFICE
            ),
        )

        academic_year = (
            AcademicYearFactory.closed(
                user=academic_user
            )
        )

        self.authenticate_with_jwt(
            user=academic_user
        )

        response = self.client.post(
            reverse(
                "academic-year-reopen",
                kwargs={
                    "pk": academic_year.pk,
                },
            ),
            {},
            format="json",
        )

        self.assert_validation_error(
            response,
            field="reason",
        )


class EducationReferenceApiTests(
    AcademicsApiBase
):
    def test_create_education_level(self):
        response = self.client.post(
            reverse("education-level-list"),
            {
                "code": "master",
                "name_ru": "Магистратура",
                "name_uz": "Magistratura",
                "is_active": True,
                "sort_order": 20,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_create_study_form(self):
        response = self.client.post(
            reverse("study-form-list"),
            {
                "code": "evening",
                "name_ru": "Вечерняя",
                "name_uz": "Kechki",
                "is_active": True,
                "sort_order": 30,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_duration_filter(self):
        expected = EducationDurationFactory()
        EducationDurationFactory(
            education_level=(
                EducationLevelFactory(
                    code="master",
                    name_ru="Магистратура",
                    name_uz="Magistratura",
                )
            ),
            study_form=StudyFormFactory(
                code="part_time",
                name_ru="Заочная",
                name_uz="Sirtqi",
            ),
            duration_months=24,
            semesters_count=4,
        )

        response = self.client.get(
            reverse(
                "education-duration-list"
            ),
            {
                "education_level": (
                    expected.education_level_id
                ),
                "study_form": (
                    expected.study_form_id
                ),
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


class AcademicSemesterApiTests(
    AcademicsApiBase
):
    def test_create_autumn_semester(self):
        academic_year = (
            AcademicYearFactory(
                start_year=2050,
                end_year=2051,
            )
        )

        response = self.client.post(
            reverse(
                "academic-semester-list"
            ),
            {
                "academic_year": (
                    academic_year.pk
                ),
                "season": "autumn",
                "start_date": "2050-09-01",
                "end_date": "2050-12-31",
                "is_current": False,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_invalid_dates_rejected(self):
        academic_year = (
            AcademicYearFactory(
                start_year=2052,
                end_year=2053,
            )
        )

        response = self.client.post(
            reverse(
                "academic-semester-list"
            ),
            {
                "academic_year": (
                    academic_year.pk
                ),
                "season": "autumn",
                "start_date": "2052-09-01",
                "end_date": "2052-08-01",
            },
            format="json",
        )

        self.assert_validation_error(
            response,
            field="end_date",
        )


class StudyProgramApiTests(
    AcademicsApiBase
):
    def test_create_program(self):
        department = DepartmentFactory()

        response = self.client.post(
            reverse("study-program-list"),
            {
                "university": (
                    department
                    .faculty
                    .university_id
                ),
                "education_level": (
                    EducationLevelFactory().pk
                ),
                "code": " 606-API ",
                "name_ru": "API направление",
                "name_uz": "API yo‘nalishi",
                "profiling_department": (
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
            "606-API",
        )

    def test_filter_by_university(self):
        expected = StudyProgramFactory()
        StudyProgramFactory()

        response = self.client.get(
            reverse("study-program-list"),
            {
                "university": (
                    expected.university_id
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


class StudentGroupApiTests(
    AcademicsApiBase
):
    def test_create_group(self):
        source = StudentGroupFactory()

        response = self.client.post(
            reverse("student-group-list"),
            {
                "academic_year_admission": (
                    source
                    .academic_year_admission_id
                ),
                "faculty": source.faculty_id,
                "study_program": (
                    source.study_program_id
                ),
                "study_form": (
                    source.study_form_id
                ),
                "code": " api-group ",
                "student_count": 30,
                "subgroup_count": 2,
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
            "API-GROUP",
        )

    def test_filter_by_faculty(self):
        expected = StudentGroupFactory()
        StudentGroupFactory()

        response = self.client.get(
            reverse("student-group-list"),
            {
                "faculty": expected.faculty_id,
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