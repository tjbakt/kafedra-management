from decimal import Decimal

from django.urls import reverse
from rest_framework import status

from apps.workload.models import (
    WorkloadDistribution,
)
from tests.assertions import (
    ApiResponseAssertionsMixin,
)
from tests.base import BaseAPITestCase
from tests.factories import (
    AcademicYearFactory,
    PlannedWorkloadFactory,
    StaffEmploymentAcademicYearFactory,
    StaffEmploymentFactory,
    WorkloadDistributionFactory,
)


class WorkloadApiBase(
    ApiResponseAssertionsMixin,
    BaseAPITestCase,
):
    def setUp(self):
        self.user = self.create_global_admin()

        self.authenticate_with_jwt(
            user=self.user
        )

        self.list_url = reverse(
            "workload-distribution-list"
        )

    def detail_url(self, distribution):
        return reverse(
            "workload-distribution-detail",
            kwargs={
                "pk": distribution.pk,
            },
        )

    def results(self, response):
        if isinstance(response.data, list):
            return response.data

        return response.data["results"]


class WorkloadDistributionCrudApiTests(
    WorkloadApiBase
):
    def test_requires_authentication(self):
        self.logout_client()

        response = self.client.get(
            self.list_url
        )

        self.assert_authentication_required(
            response
        )

    def test_create_distribution(self):
        planned = PlannedWorkloadFactory(
            total_hours=Decimal("100.00"),
        )

        employment = StaffEmploymentFactory(
            department=(
                planned.teaching_department
            ),
        )

        StaffEmploymentAcademicYearFactory(
            staff_employment=employment,
            academic_year=planned.academic_year,
        )

        response = self.client.post(
            self.list_url,
            {
                "planned_workload": planned.pk,
                "staff_employment": (
                    employment.pk
                ),
                "allocated_hours": "30.00",
                "notes": "",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        distribution = (
            WorkloadDistribution.objects.get(
                pk=response.data["id"]
            )
        )

        self.assertEqual(
            distribution.created_by,
            self.user,
        )
        self.assertEqual(
            distribution.status,
            WorkloadDistribution.Status.DRAFT,
        )

    def test_patch_draft_distribution(self):
        distribution = (
            WorkloadDistributionFactory()
        )

        response = self.client.patch(
            self.detail_url(distribution),
            {
                "allocated_hours": "20.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        distribution.refresh_from_db()

        self.assertEqual(
            distribution.allocated_hours,
            Decimal("20.00"),
        )

    def test_filter_by_academic_year(self):
        expected = (
            WorkloadDistributionFactory()
        )

        WorkloadDistributionFactory()

        response = self.client.get(
            self.list_url,
            {
                "academic_year": (
                    expected.planned_workload
                    .academic_year_id
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

    def test_archive_and_restore_archived(
        self,
    ):
        distribution = (
            WorkloadDistributionFactory()
        )

        delete_response = self.client.delete(
            self.detail_url(distribution)
        )

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_200_OK,
        )

        restore_response = self.client.post(
            reverse(
                "workload-distribution-restore-archived",
                kwargs={
                    "pk": distribution.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            restore_response.status_code,
            status.HTTP_200_OK,
        )

        distribution.refresh_from_db()

        self.assertFalse(
            distribution.is_archived,
        )


class WorkloadDistributionActionsApiTests(
    WorkloadApiBase
):
    def test_approve(self):
        distribution = (
            WorkloadDistributionFactory()
        )

        response = self.client.post(
            reverse(
                "workload-distribution-approve",
                kwargs={
                    "pk": distribution.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["data"]["status"],
            WorkloadDistribution.Status.APPROVED,
        )

    def test_cancel_requires_reason(self):
        distribution = (
            WorkloadDistributionFactory()
        )

        response = self.client.post(
            reverse(
                "workload-distribution-cancel",
                kwargs={
                    "pk": distribution.pk,
                },
            ),
            {},
            format="json",
        )

        self.assert_validation_error(
            response,
            field="reason",
        )

    def test_cancel_and_restore(self):
        distribution = (
            WorkloadDistributionFactory()
        )

        cancel_response = self.client.post(
            reverse(
                "workload-distribution-cancel",
                kwargs={
                    "pk": distribution.pk,
                },
            ),
            {
                "reason": "Ошибка назначения",
            },
            format="json",
        )

        self.assertEqual(
            cancel_response.status_code,
            status.HTTP_200_OK,
        )

        restore_response = self.client.post(
            reverse(
                "workload-distribution-restore",
                kwargs={
                    "pk": distribution.pk,
                },
            ),
            {
                "reason": "Исправлено",
            },
            format="json",
        )

        self.assertEqual(
            restore_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            restore_response.data[
                "data"
            ]["status"],
            WorkloadDistribution.Status.DRAFT,
        )

    def test_return_to_draft(self):
        distribution = (
            WorkloadDistributionFactory()
        )

        approve_response = self.client.post(
            reverse(
                "workload-distribution-approve",
                kwargs={
                    "pk": distribution.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            approve_response.status_code,
            status.HTTP_200_OK,
        )

        response = self.client.post(
            reverse(
                "workload-distribution-return-to-draft",
                kwargs={
                    "pk": distribution.pk,
                },
            ),
            {
                "reason": "Корректировка",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["data"]["status"],
            WorkloadDistribution.Status.DRAFT,
        )

    def test_available_actions(self):
        distribution = (
            WorkloadDistributionFactory()
        )

        response = self.client.get(
            reverse(
                "workload-distribution-available-actions",
                kwargs={
                    "pk": distribution.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["distribution_id"],
            distribution.pk,
        )
        self.assertEqual(
            response.data["status"],
            WorkloadDistribution.Status.DRAFT,
        )

        actions = response.data["actions"]

        self.assertIn(
            "approve",
            actions,
        )
        self.assertIn(
            "cancel",
            actions,
        )
        self.assertIn(
            "transfer",
            actions,
        )
        self.assertIn(
            "edit",
            actions,
        )
        self.assertIn(
            "restore",
            actions,
        )
        self.assertIn(
            "return_to_draft",
            actions,
        )

        self.assertTrue(
            actions["approve"]["allowed"]
        )
        self.assertTrue(
            actions["cancel"]["allowed"]
        )
        self.assertTrue(
            actions["transfer"]["allowed"]
        )
        self.assertTrue(
            actions["edit"]["allowed"]
        )

        self.assertFalse(
            actions["restore"]["allowed"]
        )
        self.assertFalse(
            actions[
                "return_to_draft"
            ]["allowed"]
        )

    def test_transfer_hours(self):
        source = WorkloadDistributionFactory(
            allocated_hours=Decimal("30.00"),
        )

        target = StaffEmploymentFactory(
            department=(
                source.planned_workload
                .teaching_department
            ),
        )

        StaffEmploymentAcademicYearFactory(
            staff_employment=target,
            academic_year=(
                source.planned_workload
                .academic_year
            ),
        )

        response = self.client.post(
            reverse(
                "workload-distribution-transfer",
                kwargs={
                    "pk": source.pk,
                },
            ),
            {
                "target_staff_employment": (
                    target.pk
                ),
                "transfer_hours": "10.00",
                "reason": "Перераспределение",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            Decimal(
                response.data["data"][
                    "transferred_hours"
                ]
            ),
            Decimal("10.00"),
        )


class WorkloadBulkActionsApiTests(
    WorkloadApiBase
):
    def test_approve_selected(self):
        first = WorkloadDistributionFactory()
        second = WorkloadDistributionFactory()

        response = self.client.post(
            reverse(
                "workload-distribution-approve-selected"
            ),
            {
                "ids": [
                    first.pk,
                    second.pk,
                ]
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["approved_count"],
            2,
        )

    def test_cancel_selected(self):
        first = WorkloadDistributionFactory()
        second = WorkloadDistributionFactory()

        response = self.client.post(
            reverse(
                "workload-distribution-cancel-selected"
            ),
            {
                "ids": [
                    first.pk,
                    second.pk,
                ],
                "reason": "Массовая корректировка",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["cancelled_count"],
            2,
        )

    def test_restore_selected(self):
        first = WorkloadDistributionFactory(
            status=(
                WorkloadDistribution
                .Status
                .CANCELLED
            ),
        )
        second = WorkloadDistributionFactory(
            status=(
                WorkloadDistribution
                .Status
                .CANCELLED
            ),
        )

        response = self.client.post(
            reverse(
                "workload-distribution-restore-selected"
            ),
            {
                "ids": [
                    first.pk,
                    second.pk,
                ],
                "reason": "Восстановление",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["restored_count"],
            2,
        )

    def test_assign_selected(
        self,
    ):
        academic_year = (
            AcademicYearFactory()
        )

        first = PlannedWorkloadFactory(
            academic_year=academic_year,
            total_hours=Decimal(
                "30.00"
            ),
        )

        second = PlannedWorkloadFactory(
            academic_year=academic_year,
            teaching_department=(
                first
                .teaching_department
            ),
            total_hours=Decimal(
                "16.00"
            ),
        )

        employment = (
            StaffEmploymentFactory(
                department=(
                    first
                    .teaching_department
                ),
            )
        )

        StaffEmploymentAcademicYearFactory(
            staff_employment=(
                employment
            ),
            academic_year=(
                academic_year
            ),
        )

        response = self.client.post(
            reverse(
                (
                    "workload-distribution-"
                    "assign-selected"
                )
            ),
            {
                "planned_workloads": [
                    first.pk,
                    second.pk,
                ],
                "staff_employment": (
                    employment.pk
                ),
                "notes": (
                    "Массовое назначение"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data[
                "created_count"
            ],
            2,
        )

        self.assertEqual(
            Decimal(
                response.data[
                    "allocated_hours"
                ]
            ),
            Decimal(
                "46.00"
            ),
        )

        distributions = (
            WorkloadDistribution
            .objects
            .filter(
                pk__in=response.data[
                    "created_ids"
                ]
            )
        )

        self.assertEqual(
            distributions.count(),
            2,
        )

        self.assertTrue(
            all(
                item.staff_employment_id
                == employment.pk
                for item
                in distributions
            )
        )

        self.assertTrue(
            all(
                item.status
                == (
                    WorkloadDistribution
                    .Status
                    .DRAFT
                )
                for item
                in distributions
            )
        )


    def test_assign_selected_rejects_different_departments(
        self,
    ):
        academic_year = (
            AcademicYearFactory()
        )

        first = PlannedWorkloadFactory(
            academic_year=academic_year,
        )

        second = PlannedWorkloadFactory(
            academic_year=academic_year,
        )

        employment = (
            StaffEmploymentFactory(
                department=(
                    first
                    .teaching_department
                ),
            )
        )

        StaffEmploymentAcademicYearFactory(
            staff_employment=(
                employment
            ),
            academic_year=(
                academic_year
            ),
        )

        response = self.client.post(
            reverse(
                (
                    "workload-distribution-"
                    "assign-selected"
                )
            ),
            {
                "planned_workloads": [
                    first.pk,
                    second.pk,
                ],
                "staff_employment": (
                    employment.pk
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assert_validation_error(
            response,
            field="planned_workloads",
        )

        # self.assertIn(
        #     "planned_workloads",
        #     response.data,
        # )


class WorkloadSummaryApiTests(
    WorkloadApiBase
):
    def test_teacher_summary_requires_year(
        self,
    ):
        response = self.client.get(
            reverse(
                "workload-distribution-teacher-summary"
            )
        )

        self.assert_validation_error(
            response,
            field="academic_year",
        )

    def test_teacher_summary(self):
        distribution = (
            WorkloadDistributionFactory()
        )

        response = self.client.get(
            reverse(
                "workload-distribution-teacher-summary"
            ),
            {
                "academic_year": (
                    distribution
                    .planned_workload
                    .academic_year_id
                )
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIsInstance(
            response.data,
            list,
        )

    def test_department_summary(self):
        distribution = (
            WorkloadDistributionFactory()
        )

        response = self.client.get(
            reverse(
                "workload-distribution-department-summary"
            ),
            {
                "academic_year": (
                    distribution
                    .planned_workload
                    .academic_year_id
                ),
                "department": (
                    distribution
                    .planned_workload
                    .teaching_department_id
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIsInstance(
            response.data,
            list,
        )

    def test_dashboard(self):
        distribution = (
            WorkloadDistributionFactory()
        )

        response = self.client.get(
            reverse(
                "workload-distribution-dashboard"
            ),
            {
                "academic_year": (
                    distribution
                    .planned_workload
                    .academic_year_id
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn(
            "workload",
            response.data,
        )
        self.assertIn(
            "teachers",
            response.data,
        )
        self.assertIn(
            "departments",
            response.data,
        )