from decimal import Decimal

from django.urls import reverse
from rest_framework import status

from apps.curriculum.models import (
    WorkloadType,
)
from apps.teaching.models import (
    PlannedWorkload,
)
from tests.assertions import (
    ApiResponseAssertionsMixin,
)
from tests.base import BaseAPITestCase
from tests.factories import (
    AcademicSemesterFactory,
    AcademicYearFactory,
    CurriculumDisciplineFactory,
    CurriculumWorkloadFactory,
    GroupCurriculumAssignmentFactory,
    GroupSemesterFactory,
    PlannedWorkloadFactory,
    TeachingStreamFactory,
    TeachingStreamGroupFactory,
    UserFactory,
    WorkloadTypeFactory,
)


class TeachingApiBase(
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


class GroupCurriculumApiTests(
    TeachingApiBase
):
    def test_requires_authentication(self):
        self.logout_client()

        response = self.client.get(
            reverse("group-curriculum-list")
        )

        self.assert_authentication_required(
            response
        )

    def test_create_assignment(self):
        source = (
            GroupCurriculumAssignmentFactory()
        )

        response = self.client.post(
            reverse("group-curriculum-list"),
            {
                "student_group": (
                    source.student_group_id
                ),
                "curriculum": (
                    source.curriculum_id
                ),
                "start_academic_year": (
                    AcademicYearFactory().pk
                ),
                "is_primary": False,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )


class GroupSemesterApiTests(
    TeachingApiBase
):
    def test_create_group_semester(self):
        assignment = (
            GroupCurriculumAssignmentFactory()
        )
        year = AcademicYearFactory()
        semester = AcademicSemesterFactory(
            academic_year=year,
        )

        response = self.client.post(
            reverse("group-semester-list"),
            {
                "group_curriculum": (
                    assignment.pk
                ),
                "academic_year": year.pk,
                "academic_semester": semester.pk,
                "semester_number": 1,
                "students_count": 25,
                "subgroup_count": 1,
                "status": "planned",
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


class TeachingStreamApiTests(
    TeachingApiBase
):
    def test_create_stream(self):
        discipline = (
            CurriculumDisciplineFactory()
        )
        workload = CurriculumWorkloadFactory(
            curriculum_discipline=discipline,
        )
        year = AcademicYearFactory()
        semester = AcademicSemesterFactory(
            academic_year=year,
        )

        response = self.client.post(
            reverse("teaching-stream-list"),
            {
                "academic_year": year.pk,
                "academic_semester": semester.pk,
                "curriculum_discipline": (
                    discipline.pk
                ),
                "curriculum_workload": (
                    workload.pk
                ),
                "teaching_department": (
                    discipline
                    .teaching_department_id
                ),
                "code": " stream-api ",
                "name": "API поток",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["code"],
            "STREAM-API",
        )

    def test_calculate_stream(self):
        workload_type = WorkloadTypeFactory(
            calculation_mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),
        )
        workload = CurriculumWorkloadFactory(
            workload_type=workload_type,
            calculation_mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),
            base_hours=Decimal("30.00"),
        )
        stream = TeachingStreamFactory(
            curriculum_discipline=(
                workload.curriculum_discipline
            ),
            curriculum_workload=workload,
            teaching_department=(
                workload
                .curriculum_discipline
                .teaching_department
            ),
        )

        TeachingStreamGroupFactory.create_batch(
            2,
            teaching_stream=stream,
        )

        response = self.client.post(
            reverse(
                "teaching-stream-calculate",
                kwargs={"pk": stream.pk},
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            Decimal(
                response.data["data"][
                    "total_hours"
                ]
            ),
            Decimal("60.00"),
        )

    def test_calculate_without_groups_rejected(
        self,
    ):
        stream = TeachingStreamFactory()

        response = self.client.post(
            reverse(
                "teaching-stream-calculate",
                kwargs={"pk": stream.pk},
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_calculate_all(self):
        valid = TeachingStreamFactory()
        TeachingStreamGroupFactory(
            teaching_stream=valid,
        )

        invalid = TeachingStreamFactory()

        response = self.client.post(
            reverse(
                "teaching-stream-calculate-all"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertGreaterEqual(
            response.data["calculated_count"],
            1,
        )
        self.assertGreaterEqual(
            response.data["errors_count"],
            1,
        )


class PlannedWorkloadApiTests(
    TeachingApiBase
):
    def test_post_is_not_allowed(self):
        response = self.client.post(
            reverse("planned-workload-list"),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_summary(self):
        first = PlannedWorkloadFactory(
            total_hours=Decimal("30.00"),
        )
        PlannedWorkloadFactory(
            teaching_stream=(
                TeachingStreamFactory(
                    teaching_department=(
                        first.teaching_department
                    ),
                )
            ),
            total_hours=Decimal("20.00"),
        )

        response = self.client.get(
            reverse(
                "planned-workload-summary"
            ),
            {
                "teaching_department": (
                    first.teaching_department_id
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            Decimal(
                response.data["total_hours"]
            ),
            Decimal("50.00"),
        )

    def test_archive_and_restore(self):
        workload = PlannedWorkloadFactory()

        delete_response = self.client.delete(
            reverse(
                "planned-workload-detail",
                kwargs={"pk": workload.pk},
            )
        )

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_200_OK,
        )

        restore_response = self.client.post(
            reverse(
                "planned-workload-restore",
                kwargs={"pk": workload.pk},
            ),
            {},
            format="json",
        )

        self.assertEqual(
            restore_response.status_code,
            status.HTTP_200_OK,
        )

        workload.refresh_from_db()

        self.assertFalse(
            workload.is_archived
        )