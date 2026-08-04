from django.utils import timezone
from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

from apps.access_control.models import (
    SystemRole,
)
from apps.individual_plan.models import (
    IndividualPlan,
    IndividualPlanItem,
    IndividualPlanSection,
    IndividualPlanTeachingWorkload,
)
from apps.workload.models import (
    WorkloadDistribution,
)
from tests.assertions import (
    ApiResponseAssertionsMixin,
)
from tests.base import BaseAPITestCase
from tests.factories import (
    AcademicSemesterFactory,
    AcademicYearFactory,
    DepartmentFactory,
    IndividualActivityTypeFactory,
    IndividualPlanFactory,
    IndividualPlanItemFactory,
    IndividualPlanSectionFactory,
    StaffEmploymentFactory,
    StaffMemberFactory,
    StaffPositionFactory,
    UserFactory,
    UserRoleAssignmentFactory,
    WorkloadDistributionFactory,
)


class IndividualPlanApiBase(
    ApiResponseAssertionsMixin,
    BaseAPITestCase,
):
    def setUp(self):
        self.user = self.create_global_admin()

        self.authenticate_with_jwt(
            user=self.user
        )

    def results(self, response):
        if isinstance(response.data, list):
            return response.data

        return response.data["results"]

    def plan_detail_url(self, plan):
        return reverse(
            "individual-plan-detail",
            kwargs={
                "pk": plan.pk,
            },
        )

    def item_detail_url(self, item):
        return reverse(
            "individual-plan-item-detail",
            kwargs={
                "pk": item.pk,
            },
        )


class IndividualPlanReferenceApiTests(
    IndividualPlanApiBase
):
    def test_sections_require_authentication(
        self,
    ):
        self.logout_client()

        response = self.client.get(
            reverse(
                "individual-plan-section-list"
            )
        )

        self.assert_authentication_required(
            response
        )

    def test_create_section(self):
        response = self.client.post(
            reverse(
                "individual-plan-section-list"
            ),
            {
                "code": (
                    IndividualPlanSection
                    .Code
                    .SCIENTIFIC
                ),
                "name_ru": "Научная работа",
                "name_uz": "Ilmiy ish",
                "is_hourly": True,
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
            response.data["code"],
            (
                IndividualPlanSection
                .Code
                .SCIENTIFIC
            ),
        )

    def test_create_activity_type(self):
        section = (
            IndividualPlanSectionFactory(
                code=(
                    IndividualPlanSection
                    .Code
                    .SCIENTIFIC
                ),
                name_ru="Научная работа",
                name_uz="Ilmiy ish",
            )
        )

        response = self.client.post(
            reverse(
                "individual-activity-type-list"
            ),
            {
                "section": section.pk,
                "code": " article-api ",
                "name_ru": "Публикация статьи",
                "name_uz": "Maqola nashri",
                "default_hours": "30.00",
                "requires_evidence": True,
                "is_active": True,
                "sort_order": 10,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["code"],
            "ARTICLE-API",
        )

    def test_filter_activity_by_section(self):
        section = (
            IndividualPlanSectionFactory(
                code=(
                    IndividualPlanSection
                    .Code
                    .SCIENTIFIC
                ),
                name_ru="Научная работа",
                name_uz="Ilmiy ish",
            )
        )

        expected = (
            IndividualActivityTypeFactory(
                section=section,
            )
        )

        IndividualActivityTypeFactory(
            section=(
                IndividualPlanSectionFactory(
                    code=(
                        IndividualPlanSection
                        .Code
                        .METHODOLOGICAL
                    ),
                    name_ru=(
                        "Учебно-методическая "
                        "работа"
                    ),
                    name_uz=(
                        "O‘quv-uslubiy ish"
                    ),
                )
            )
        )

        response = self.client.get(
            reverse(
                "individual-activity-type-list"
            ),
            {
                "section": section.pk,
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


class IndividualPlanCrudApiTests(
    IndividualPlanApiBase
):
    def test_plans_require_authentication(
        self,
    ):
        self.logout_client()

        response = self.client.get(
            reverse("individual-plan-list")
        )

        self.assert_authentication_required(
            response
        )

    def test_create_plan(self):
        employment = StaffEmploymentFactory(
            position=StaffPositionFactory(
                is_teaching_position=True,
            ),
            is_active=True,
        )
        academic_year = AcademicYearFactory()

        response = self.client.post(
            reverse("individual-plan-list"),
            {
                "staff_employment": (
                    employment.pk
                ),
                "academic_year": (
                    academic_year.pk
                ),
                "teacher_notes": (
                    "План преподавателя"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["status"],
            IndividualPlan.Status.DRAFT,
        )

        plan = IndividualPlan.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            plan.created_by,
            self.user,
        )

    def test_duplicate_plan_rejected(self):
        existing = IndividualPlanFactory()

        response = self.client.post(
            reverse("individual-plan-list"),
            {
                "staff_employment": (
                    existing.staff_employment_id
                ),
                "academic_year": (
                    existing.academic_year_id
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_patch_draft_plan(self):
        plan = IndividualPlanFactory()

        response = self.client.patch(
            self.plan_detail_url(plan),
            {
                "teacher_notes": (
                    "Обновлённое примечание"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        plan.refresh_from_db()

        self.assertEqual(
            plan.teacher_notes,
            "Обновлённое примечание",
        )

    def test_filter_by_academic_year(self):
        expected = IndividualPlanFactory()

        IndividualPlanFactory()

        response = self.client.get(
            reverse("individual-plan-list"),
            {
                "academic_year": (
                    expected.academic_year_id
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

    def test_filter_by_department(self):
        expected = IndividualPlanFactory()

        IndividualPlanFactory()

        response = self.client.get(
            reverse("individual-plan-list"),
            {
                "department": (
                    expected
                    .staff_employment
                    .department_id
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

    def test_archive_and_restore(self):
        plan = IndividualPlanFactory()

        delete_response = self.client.delete(
            self.plan_detail_url(plan)
        )

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_200_OK,
        )

        restore_response = self.client.post(
            reverse(
                "individual-plan-restore",
                kwargs={
                    "pk": plan.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            restore_response.status_code,
            status.HTTP_200_OK,
        )

        plan.refresh_from_db()

        self.assertFalse(plan.is_archived)


class IndividualPlanAccessApiTests(
    IndividualPlanApiBase
):
    def create_teacher_plan(self):
        teacher_user = UserFactory()

        staff_member = StaffMemberFactory(
            user=teacher_user,
            created_by=teacher_user,
            updated_by=teacher_user,
        )

        employment = StaffEmploymentFactory(
            staff_member=staff_member,
            position=StaffPositionFactory(
                is_teaching_position=True,
            ),
            created_by=teacher_user,
            updated_by=teacher_user,
        )

        UserRoleAssignmentFactory.self_role(
            user=teacher_user,
            staff_member=staff_member,
            role_code=SystemRole.Code.TEACHER,
        )

        plan = IndividualPlanFactory(
            staff_employment=employment,
            created_by=teacher_user,
            updated_by=teacher_user,
        )

        return teacher_user, plan

    def test_teacher_sees_own_plan(self):
        teacher_user, plan = (
            self.create_teacher_plan()
        )

        IndividualPlanFactory()

        self.authenticate_with_jwt(
            user=teacher_user
        )

        response = self.client.get(
            reverse("individual-plan-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertIn(plan.pk, ids)

    def test_teacher_can_edit_own_draft(
        self,
    ):
        teacher_user, plan = (
            self.create_teacher_plan()
        )

        self.authenticate_with_jwt(
            user=teacher_user
        )

        response = self.client.patch(
            self.plan_detail_url(plan),
            {
                "teacher_notes": (
                    "Обновлено преподавателем"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_teacher_cannot_edit_approved_plan(
        self,
    ):
        teacher_user, plan = (
            self.create_teacher_plan()
        )

        plan.status = (
            IndividualPlan.Status.APPROVED
        )
        plan.save(
            update_fields=("status",)
        )

        self.authenticate_with_jwt(
            user=teacher_user
        )

        response = self.client.patch(
            self.plan_detail_url(plan),
            {
                "teacher_notes": "Изменение",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_department_head_sees_department_plan(
        self,
    ):
        plan = IndividualPlanFactory()
        head_user = UserFactory()

        UserRoleAssignmentFactory.department_role(
            user=head_user,
            department=(
                plan.staff_employment.department
            ),
            role_code=(
                SystemRole.Code.DEPARTMENT_HEAD
            ),
        )

        hidden = IndividualPlanFactory()

        self.assertNotEqual(
            hidden.staff_employment.department_id,
            plan.staff_employment.department_id,
        )

        self.authenticate_with_jwt(
            user=head_user
        )

        response = self.client.get(
            reverse("individual-plan-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertIn(plan.pk, ids)
        self.assertNotIn(hidden.pk, ids)


class IndividualPlanItemCrudApiTests(
    IndividualPlanApiBase
):
    def test_create_item(self):
        plan = IndividualPlanFactory()
        section = (
            IndividualPlanSectionFactory()
        )
        activity = (
            IndividualActivityTypeFactory(
                section=section,
            )
        )
        semester = AcademicSemesterFactory(
            academic_year=plan.academic_year,
        )

        response = self.client.post(
            reverse(
                "individual-plan-item-list"
            ),
            {
                "individual_plan": plan.pk,
                "section": section.pk,
                "activity_type": activity.pk,
                "academic_semester": semester.pk,
                "title": "Подготовка материала",
                "description": "",
                "planned_hours": "20.00",
                "actual_hours": "0.00",
                "expected_result": (
                    "Учебный материал"
                ),
                "status": (
                    IndividualPlanItem
                    .Status
                    .PLANNED
                ),
                "sort_order": 10,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        item = IndividualPlanItem.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            item.created_by,
            self.user,
        )

    def test_patch_item(self):
        section = (
            IndividualPlanSectionFactory()
        )
        activity = (
            IndividualActivityTypeFactory(
                section=section,
            )
        )

        item = IndividualPlanItemFactory(
            section=section,
            activity_type=activity,
            academic_semester=None,
        )

        response = self.client.patch(
            self.item_detail_url(item),
            {
                "title": (
                    "Обновлённое название"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        item.refresh_from_db()

        self.assertEqual(
            item.title,
            "Обновлённое название",
        )

    def test_filter_items_by_plan(self):
        expected = IndividualPlanItemFactory(
            academic_semester=None,
        )

        IndividualPlanItemFactory(
            academic_semester=None,
        )

        response = self.client.get(
            reverse(
                "individual-plan-item-list"
            ),
            {
                "individual_plan": (
                    expected.individual_plan_id
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


class IndividualPlanWorkflowApiTests(
    IndividualPlanApiBase
):
    @patch(
        (
            "apps.individual_plan.services."
            "plan_service."
            "AccessService.users_with_role"
        ),
        return_value=[],
    )
    def test_submit_plan(
        self,
        mocked_users,
    ):
        plan = IndividualPlanFactory()

        IndividualPlanItemFactory(
            individual_plan=plan,
            academic_semester=None,
        )

        response = self.client.post(
            reverse(
                "individual-plan-submit",
                kwargs={
                    "pk": plan.pk,
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
            response.data["status"],
            IndividualPlan.Status.SUBMITTED,
        )

        plan.refresh_from_db()

        self.assertIsNotNone(
            plan.submitted_at
        )

    def test_empty_plan_cannot_be_submitted(
        self,
    ):
        plan = IndividualPlanFactory()

        response = self.client.post(
            reverse(
                "individual-plan-submit",
                kwargs={
                    "pk": plan.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_approve_submitted_plan(self):
        plan = IndividualPlanFactory(
            status=(
                IndividualPlan.Status.SUBMITTED
            ),
        )

        response = self.client.post(
            reverse(
                "individual-plan-approve",
                kwargs={
                    "pk": plan.pk,
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
            response.data["status"],
            IndividualPlan.Status.APPROVED,
        )

        plan.refresh_from_db()

        self.assertEqual(
            plan.approved_by,
            self.user,
        )
        self.assertIsNotNone(
            plan.approved_at
        )

    def test_return_requires_notes(self):
        plan = IndividualPlanFactory(
            status=(
                IndividualPlan.Status.SUBMITTED
            ),
        )

        response = self.client.post(
            reverse(
                "individual-plan-return-for-revision",
                kwargs={
                    "pk": plan.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "reviewer_notes",
            response.data,
        )

    def test_return_plan_for_revision(self):
        plan = IndividualPlanFactory(
            status=(
                IndividualPlan.Status.SUBMITTED
            ),
        )

        response = self.client.post(
            reverse(
                "individual-plan-return-for-revision",
                kwargs={
                    "pk": plan.pk,
                },
            ),
            {
                "reviewer_notes": (
                    "Необходимо уточнить часы."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["status"],
            IndividualPlan.Status.RETURNED,
        )

        plan.refresh_from_db()

        self.assertEqual(
            plan.reviewer_notes,
            "Необходимо уточнить часы.",
        )


class TeachingWorkloadImportApiTests(
    IndividualPlanApiBase
):
    def test_import_approved_distribution(
        self,
    ):
        plan = IndividualPlanFactory()

        IndividualPlanSectionFactory(
            code=(
                IndividualPlanSection
                .Code
                .TEACHING
            ),
        )

        distribution = (
            WorkloadDistributionFactory(
                staff_employment=(
                    plan.staff_employment
                ),
                planned_workload__academic_year=(
                    plan.academic_year
                ),
                status=(
                    WorkloadDistribution
                    .Status
                    .APPROVED
                ),
                allocated_hours=(
                    Decimal("30.00")
                ),
            )
        )

        response = self.client.post(
            reverse(
                (
                    "individual-plan-"
                    "import-teaching-workload"
                ),
                kwargs={
                    "pk": plan.pk,
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
            response.data["created_count"],
            1,
        )

        link = (
            IndividualPlanTeachingWorkload
            .objects
            .get(
                workload_distribution=(
                    distribution
                )
            )
        )

        self.assertEqual(
            link.plan_item.individual_plan,
            plan,
        )
        self.assertEqual(
            link.imported_hours,
            Decimal("30.00"),
        )

    def test_draft_distribution_not_imported(
        self,
    ):
        plan = IndividualPlanFactory()

        IndividualPlanSectionFactory(
            code=(
                IndividualPlanSection
                .Code
                .TEACHING
            ),
        )

        WorkloadDistributionFactory(
            staff_employment=(
                plan.staff_employment
            ),
            planned_workload__academic_year=(
                plan.academic_year
            ),
            status=(
                WorkloadDistribution
                .Status
                .DRAFT
            ),
        )

        response = self.client.post(
            reverse(
                (
                    "individual-plan-"
                    "import-teaching-workload"
                ),
                kwargs={
                    "pk": plan.pk,
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
            response.data["created_count"],
            0,
        )


class IndividualPlanItemWorkflowApiTests(
    IndividualPlanApiBase
):
    @patch(
        (
            "apps.individual_plan.api.views."
            "AccessService.users_with_role"
        ),
        return_value=[],
    )
    def test_complete_item(
        self,
        mocked_users,
    ):
        section = (
            IndividualPlanSectionFactory()
        )
        activity = (
            IndividualActivityTypeFactory(
                section=section,
                requires_evidence=False,
            )
        )

        item = IndividualPlanItemFactory(
            section=section,
            activity_type=activity,
            academic_semester=None,
            status=(
                IndividualPlanItem
                .Status
                .PLANNED
            ),
        )

        response = self.client.post(
            reverse(
                "individual-plan-item-complete",
                kwargs={
                    "pk": item.pk,
                },
            ),
            {
                "actual_hours": "18.00",
                "actual_result": (
                    "Работа выполнена"
                ),
                "actual_completion_date": (
                    date.today().isoformat()
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["status"],
            (
                IndividualPlanItem
                .Status
                .COMPLETED
            ),
        )

        item.refresh_from_db()

        self.assertEqual(
            item.actual_hours,
            Decimal("18.00"),
        )
        self.assertEqual(
            item.actual_result,
            "Работа выполнена",
        )
        self.assertIsNotNone(
            item.actual_completion_date
        )

    def test_complete_item_requires_evidence(
        self,
    ):
        section = (
            IndividualPlanSectionFactory()
        )
        activity = (
            IndividualActivityTypeFactory(
                section=section,
                requires_evidence=True,
            )
        )

        item = IndividualPlanItemFactory(
            section=section,
            activity_type=activity,
            academic_semester=None,
        )

        response = self.client.post(
            reverse(
                "individual-plan-item-complete",
                kwargs={
                    "pk": item.pk,
                },
            ),
            {
                "actual_hours": "20.00",
                "actual_result": (
                    "Работа выполнена"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_confirm_completed_item(self):
        item = (
            IndividualPlanItemFactory.completed(
                academic_semester=None,
            )
        )

        response = self.client.post(
            reverse(
                "individual-plan-item-confirm",
                kwargs={
                    "pk": item.pk,
                },
            ),
            {
                "reviewer_comment": (
                    "Выполнение подтверждено."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["status"],
            (
                IndividualPlanItem
                .Status
                .CONFIRMED
            ),
        )

        item.refresh_from_db()

        self.assertEqual(
            item.confirmed_by,
            self.user,
        )
        self.assertIsNotNone(
            item.confirmed_at
        )

    def test_confirm_planned_item_rejected(
        self,
    ):
        item = IndividualPlanItemFactory(
            academic_semester=None,
            status=(
                IndividualPlanItem
                .Status
                .PLANNED
            ),
        )

        response = self.client.post(
            reverse(
                "individual-plan-item-confirm",
                kwargs={
                    "pk": item.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_reject_requires_comment(self):
        item = (
            IndividualPlanItemFactory.completed(
                academic_semester=None,
            )
        )

        response = self.client.post(
            reverse(
                "individual-plan-item-reject",
                kwargs={
                    "pk": item.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "reviewer_comment",
            response.data,
        )

    def test_reject_completed_item(self):
        item = (
            IndividualPlanItemFactory.completed(
                academic_semester=None,
            )
        )

        response = self.client.post(
            reverse(
                "individual-plan-item-reject",
                kwargs={
                    "pk": item.pk,
                },
            ),
            {
                "reviewer_comment": (
                    "Недостаточно подтверждений."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["status"],
            (
                IndividualPlanItem
                .Status
                .REJECTED
            ),
        )

        item.refresh_from_db()

        self.assertEqual(
            item.reviewer_comment,
            "Недостаточно подтверждений.",
        )


class IndividualPlanSummaryApiTests(
    IndividualPlanApiBase
):
    def test_plan_summary(self):
        plan = IndividualPlanFactory()

        teaching = (
            IndividualPlanSectionFactory()
        )
        scientific = (
            IndividualPlanSectionFactory(
                code=(
                    IndividualPlanSection
                    .Code
                    .SCIENTIFIC
                ),
                name_ru="Научная работа",
                name_uz="Ilmiy ish",
            )
        )

        IndividualPlanItemFactory(
            individual_plan=plan,
            section=teaching,
            activity_type=(
                IndividualActivityTypeFactory(
                    section=teaching,
                )
            ),
            academic_semester=None,
            planned_hours=Decimal("20.00"),
            actual_hours=Decimal("10.00"),
            status=(
                IndividualPlanItem
                .Status
                .COMPLETED
            ),
            actual_completion_date=(
                date.today()
            ),
        )

        IndividualPlanItemFactory(
            individual_plan=plan,
            section=scientific,
            activity_type=(
                IndividualActivityTypeFactory(
                    section=scientific,
                )
            ),
            academic_semester=None,
            planned_hours=Decimal("30.00"),
            actual_hours=Decimal("30.00"),
            status=(
                IndividualPlanItem
                .Status
                .CONFIRMED
            ),
            actual_completion_date=(
                date.today()
            ),
            confirmed_at=timezone.now(),
            confirmed_by=self.user,
        )

        response = self.client.get(
            reverse(
                "individual-plan-summary",
                kwargs={
                    "pk": plan.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            Decimal(
                response.data["planned_hours"]
            ),
            Decimal("50.00"),
        )
        self.assertEqual(
            Decimal(
                response.data["actual_hours"]
            ),
            Decimal("40.00"),
        )
        self.assertEqual(
            Decimal(
                response.data["confirmed_hours"]
            ),
            Decimal("30.00"),
        )
        self.assertEqual(
            Decimal(
                response.data[
                    "completion_percent"
                ]
            ),
            Decimal("80.00"),
        )
        self.assertEqual(
            len(response.data["by_section"]),
            2,
        )