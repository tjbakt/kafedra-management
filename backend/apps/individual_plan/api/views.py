from decimal import Decimal

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db.models import (Sum, Q)
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.api.viewsets import BaseArchiveModelViewSet
from apps.individual_plan.api.filters import (
    IndividualActivityTypeFilter,
    IndividualPlanFilter,
    IndividualPlanItemFilter,
    IndividualPlanSectionFilter,
)
from apps.individual_plan.api.serializers import (
    IndividualActivityTypeSerializer,
    IndividualPlanItemSerializer,
    IndividualPlanSectionSerializer,
    IndividualPlanSerializer,
)
from apps.individual_plan.models import (
    IndividualActivityType,
    IndividualPlan,
    IndividualPlanItem,
    IndividualPlanSection,
)
from apps.individual_plan.services.plan_service import (
    IndividualPlanService,
)

from apps.access_control.models import SystemRole
from apps.access_control.services.access_service import (
    AccessService,
)

from apps.access_control.permissions import (
    CanApproveIndividualPlan,
    CanEditIndividualPlan,
)

from apps.audit.models import AuditEvent
from apps.audit.services.audit_service import AuditService

from apps.access_control.models import SystemRole
from apps.access_control.services.access_service import (
    AccessService,
)
from apps.notifications.models import (Notification, UserTask)
from apps.notifications.services.notification_service import (
    NotificationService,
)


class IndividualPlanSectionViewSet(
    BaseArchiveModelViewSet
):
    model = IndividualPlanSection
    queryset = IndividualPlanSection.objects.all()
    serializer_class = IndividualPlanSectionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = IndividualPlanSectionFilter
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
    )
    ordering = (
        "sort_order",
        "name_ru",
    )


class IndividualActivityTypeViewSet(
    BaseArchiveModelViewSet
):
    model = IndividualActivityType
    serializer_class = IndividualActivityTypeSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = IndividualActivityTypeFilter
    search_fields = (
        "code",
        "name_ru",
        "name_uz",
        "section__name_ru",
    )
    ordering = (
        "section__sort_order",
        "sort_order",
        "name_ru",
    )

    def get_queryset(self):
        return IndividualActivityType.objects.select_related(
            "section",
        )

class IndividualPlanItemViewSet(
    BaseArchiveModelViewSet
):
    model = IndividualPlanItem
    serializer_class = IndividualPlanItemSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = IndividualPlanItemFilter
    search_fields = (
        "title",
        "description",
        "expected_result",
        "actual_result",
        "individual_plan__staff_employment__"
        "staff_member__last_name",
    )
    ordering_fields = (
        "planned_hours",
        "actual_hours",
        "planned_end_date",
        "actual_completion_date",
        "sort_order",
    )
    ordering = (
        "section__sort_order",
        "sort_order",
        "planned_end_date",
    )

    def get_queryset(self):
        return (
            IndividualPlanItem.objects
            .select_related(
                "individual_plan",
                "individual_plan__academic_year",
                "individual_plan__staff_employment",
                "individual_plan__staff_employment__staff_member",
                "section",
                "activity_type",
                "academic_semester",
                "confirmed_by",
            )
            .select_related(
                "teaching_workload_link",
                "teaching_workload_link__workload_distribution",
            )
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="complete",
    )
    def complete(self, request, pk=None):
        item = self.get_object()

        actual_hours = request.data.get(
            "actual_hours",
            item.planned_hours,
        )
        actual_result = request.data.get(
            "actual_result",
            "",
        )
        evidence_url = request.data.get(
            "evidence_url",
            "",
        )
        evidence_document = request.data.get(
            "evidence_document",
            "",
        )

        item.actual_hours = actual_hours
        item.actual_result = actual_result
        item.evidence_url = evidence_url
        item.evidence_document = evidence_document
        item.actual_completion_date = (
            request.data.get("actual_completion_date")
            or timezone.localdate()
        )
        item.status = IndividualPlanItem.Status.COMPLETED
        item.updated_by = request.user

        old_values = {
            "status": item.status,
            "actual_hours": item.actual_hours,
            "actual_result": item.actual_result,
            "actual_completion_date": (
                item.actual_completion_date
            ),
        }

        try:
            item.full_clean()
            item.save()
        except DjangoValidationError as exc:
            raise ValidationError(
                getattr(exc, "message_dict", exc.messages)
            ) from exc

        AuditService.log(
            instance=item,
            action=AuditEvent.Action.COMPLETE,
            actor=request.user,
            action_label="Пункт индивидуального плана выполнен",
            old_values=old_values,
            new_values={
                "status": item.status,
                "actual_hours": item.actual_hours,
                "actual_result": item.actual_result,
                "actual_completion_date": (
                    item.actual_completion_date
                ),
                "evidence_url": item.evidence_url,
                "evidence_document": (
                    item.evidence_document
                ),
            },
            changed_fields=[
                "status",
                "actual_hours",
                "actual_result",
                "actual_completion_date",
                "evidence_url",
                "evidence_document",
            ],
        )

        department_id = (
            item.individual_plan.staff_employment.department_id
        )

        department_heads = AccessService.users_with_role(
            role_code=SystemRole.Code.DEPARTMENT_HEAD,
            department_id=department_id,
        )

        for department_head in department_heads:
            NotificationService.create_task(
                assignee=department_head,
                task_type=UserTask.Type.CONFIRM_PLAN_ITEM,
                title="Подтвердить выполнение пункта плана",
                description=(
                    f"{item.individual_plan.teacher_name} "
                    f"отметил выполнение: {item.title}"
                ),
                priority=UserTask.Priority.NORMAL,
                instance=item,
                action_url=(
                    f"/individual-plans/"
                    f"{item.individual_plan_id}/items/"
                    f"{item.pk}/review"
                ),
                created_by=request.user,
                deduplication_key=(
                    f"confirm-individual-plan-item-{item.pk}"
                ),
            )

        return Response(
            self.get_serializer(item).data
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="confirm",
    )
    def confirm(self, request, pk=None):
        item = self.get_object()

        if item.status != IndividualPlanItem.Status.COMPLETED:
            return Response(
                {
                    "detail": (
                        "Подтвердить можно только выполненный пункт."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        item.status = IndividualPlanItem.Status.CONFIRMED
        item.confirmed_at = timezone.now()
        item.confirmed_by = request.user
        item.reviewer_comment = request.data.get(
            "reviewer_comment",
            "",
        )
        item.updated_by = request.user

        old_status = item.status

        try:
            item.full_clean()
            item.save()
        except DjangoValidationError as exc:
            raise ValidationError(
                getattr(exc, "message_dict", exc.messages)
            ) from exc

        AuditService.log_status_change(
            instance=item,
            old_status=old_status,
            new_status=item.status,
            actor=request.user,
            action=AuditEvent.Action.CONFIRM,
            action_label=(
                "Выполнение пункта индивидуального плана подтверждено"
            ),
            reason=item.reviewer_comment,
            metadata={
                "confirmed_at": item.confirmed_at,
                "confirmed_by": item.confirmed_by_id,
                "actual_hours": item.actual_hours,
            },
        )

        NotificationService.complete_tasks_for_object(
            instance=item,
            task_types=(
                UserTask.Type.CONFIRM_PLAN_ITEM,
            ),
            completion_comment=(
                "Выполнение пункта подтверждено."
            ),
        )

        teacher_user = (
            item.individual_plan
            .staff_employment
            .staff_member
            .user
        )

        if teacher_user:
            NotificationService.notify(
                recipient=teacher_user,
                title="Выполнение подтверждено",
                message=(
                    f"Выполнение пункта «{item.title}» "
                    f"подтверждено."
                ),
                notification_type=Notification.Type.SUCCESS,
                instance=item,
                action_url=(
                    f"/individual-plans/"
                    f"{item.individual_plan_id}"
                ),
            )

        return Response(
            self.get_serializer(item).data
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="reject",
    )
    def reject(self, request, pk=None):
        item = self.get_object()

        reviewer_comment = request.data.get(
            "reviewer_comment",
            "",
        ).strip()

        if not reviewer_comment:
            return Response(
                {
                    "reviewer_comment": (
                        "Укажите причину отклонения."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        old_status = item.status

        item.status = IndividualPlanItem.Status.REJECTED
        item.confirmed_at = None
        item.confirmed_by = None
        item.reviewer_comment = reviewer_comment
        item.updated_by = request.user
        item.save()

        AuditService.log_status_change(
            instance=item,
            old_status=old_status,
            new_status=item.status,
            actor=request.user,
            action=AuditEvent.Action.REJECT,
            action_label=(
                "Выполнение пункта индивидуального плана отклонено"
            ),
            reason=reviewer_comment,
        )

        NotificationService.complete_tasks_for_object(
            instance=item,
            task_types=(
                UserTask.Type.CONFIRM_PLAN_ITEM,
            ),
            completion_comment=(
                "Выполнение пункта отклонено."
            ),
        )

        teacher_user = (
            item.individual_plan
            .staff_employment
            .staff_member
            .user
        )

        if teacher_user:
            NotificationService.create_task(
                assignee=teacher_user,
                task_type=UserTask.Type.UPDATE_PLAN,
                title="Исправить данные о выполнении",
                description=(
                    f"Выполнение пункта «{item.title}» "
                    f"не подтверждено. "
                    f"Комментарий: {reviewer_comment}"
                ),
                priority=UserTask.Priority.HIGH,
                instance=item,
                action_url=(
                    f"/individual-plans/"
                    f"{item.individual_plan_id}/items/"
                    f"{item.pk}/edit"
                ),
                created_by=request.user,
                deduplication_key=(
                    f"update-individual-plan-item-{item.pk}"
                ),
            )

        return Response(
            self.get_serializer(item).data
        )

class IndividualPlanViewSet(BaseArchiveModelViewSet):
    queryset = IndividualPlan.objects.none()
    model = IndividualPlan
    serializer_class = IndividualPlanSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = IndividualPlanFilter
    search_fields = (
        "staff_employment__staff_member__personnel_number",
        "staff_employment__staff_member__last_name",
        "staff_employment__staff_member__first_name",
        "staff_employment__department__name_ru",
    )
    ordering_fields = (
        "academic_year__start_year",
        "staff_employment__staff_member__last_name",
        "status",
        "created_at",
    )
    ordering = (
        "-academic_year__start_year",
        "staff_employment__staff_member__last_name",
    )

    def get_queryset(self):
        if getattr(
                self,
                "swagger_fake_view",
                False,
        ):
            return IndividualPlan.objects.none()
        queryset = (
            IndividualPlan.objects
            .select_related(
                "staff_employment",
                "staff_employment__staff_member",
                "staff_employment__position",
                "staff_employment__department",
                "academic_year",
                "approved_by",
            )
            .prefetch_related(
                "items",
                "items__section",
                "items__activity_type",
                "items__academic_semester",
            ),

            IndividualPlanItem.objects
            .select_related(
                "individual_plan",
                "individual_plan__academic_year",
                "individual_plan__staff_employment",
                "individual_plan__staff_employment__staff_member",
                "individual_plan__staff_employment__department",
                "section",
                "activity_type",
                "academic_semester",
                "confirmed_by",
            )
            .select_related(
                "teaching_workload_link",
                "teaching_workload_link__workload_distribution",
            ),
        )

        user = self.request.user

        if user.is_superuser:
            return queryset

        if AccessService.has_global_role(
                user,
                SystemRole.Code.SYSTEM_ADMIN,
                SystemRole.Code.ACADEMIC_OFFICE,
        ):
            return queryset

        department_ids = (
            AccessService.accessible_department_ids(
                user,
                role_codes=(
                    SystemRole.Code.DEPARTMENT_HEAD,
                ),
            )
        )

        own_staff_ids = (
            AccessService.accessible_staff_member_ids(user)
        )

        if department_ids is None or own_staff_ids is None:
            return queryset

        return queryset.filter(
            Q(
                individual_plan__staff_employment__,
                department_id__in = department_ids
            )
            | Q(
                individual_plan__staff_employment__,
                staff_member_id__in = own_staff_ids
            )
        ).distinct()

    @action(
        detail=True,
        methods=["post"],
        url_path="import-teaching-workload",
    )
    def import_teaching_workload(self, request, pk=None):
        plan = self.get_object()

        try:
            result = (
                IndividualPlanService
                .import_teaching_workload(
                    plan=plan,
                    user=request.user,
                )
            )
        except DjangoValidationError as exc:
            raise ValidationError(
                getattr(exc, "message_dict", exc.messages)
            ) from exc

        return Response(
            {
                "detail": (
                    "Учебная нагрузка импортирована."
                ),
                **result,
            }
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="submit",
    )
    def submit(self, request, pk=None):
        plan = self.get_object()

        try:
            plan = IndividualPlanService.submit_plan(
                plan=plan,
                user=request.user,
            )
        except DjangoValidationError as exc:
            raise ValidationError(
                getattr(exc, "message_dict", exc.messages)
            ) from exc

        return Response(
            self.get_serializer(plan).data
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="approve",
    )
    def approve(self, request, pk=None):
        plan = self.get_object()

        try:
            plan = IndividualPlanService.approve_plan(
                plan=plan,
                user=request.user,
            )
        except DjangoValidationError as exc:
            raise ValidationError(
                getattr(exc, "message_dict", exc.messages)
            ) from exc

        return Response(
            self.get_serializer(plan).data
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="return",
    )
    def return_for_revision(self, request, pk=None):
        plan = self.get_object()

        reviewer_notes = request.data.get(
            "reviewer_notes",
            "",
        )

        if not reviewer_notes.strip():
            return Response(
                {
                    "reviewer_notes": (
                        "Укажите причину возврата плана."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            plan = IndividualPlanService.return_plan(
                plan=plan,
                reviewer_notes=reviewer_notes,
                user=request.user,
            )
        except DjangoValidationError as exc:
            raise ValidationError(
                getattr(exc, "message_dict", exc.messages)
            ) from exc

        return Response(
            self.get_serializer(plan).data
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="summary",
    )
    def summary(self, request, pk=None):
        plan = self.get_object()

        by_section = (
            plan.items
            .filter(
                is_archived=False,
                status__in=(
                    IndividualPlanItem.Status.PLANNED,
                    IndividualPlanItem.Status.IN_PROGRESS,
                    IndividualPlanItem.Status.COMPLETED,
                    IndividualPlanItem.Status.CONFIRMED,
                ),
            )
            .values(
                "section_id",
                "section__code",
                "section__name_ru",
            )
            .annotate(
                planned_hours=Sum("planned_hours"),
                actual_hours=Sum("actual_hours"),
            )
            .order_by("section__sort_order")
        )

        confirmed_hours = (
            plan.items
            .filter(
                is_archived=False,
                status=IndividualPlanItem.Status.CONFIRMED,
            )
            .aggregate(
                total=Sum("actual_hours")
            )["total"]
            or Decimal("0.00")
        )

        return Response(
            {
                "individual_plan": plan.id,
                "teacher_name": plan.teacher_name,
                "academic_year": plan.academic_year_id,
                "academic_year_name": plan.academic_year.name,
                "planned_hours": plan.planned_hours,
                "actual_hours": plan.actual_hours,
                "confirmed_hours": confirmed_hours,
                "completion_percent": plan.completion_percent,
                "by_section": list(by_section),
            }
        )

    def get_permissions(self):
        if self.action in (
                "update",
                "partial_update",
                "destroy",
                "import_teaching_workload",
                "submit",
        ):
            permission_classes = [
                IsAuthenticated,
                CanEditIndividualPlan,
            ]
        elif self.action in (
                "approve",
                "return_for_revision",
        ):
            permission_classes = [
                IsAuthenticated,
                CanApproveIndividualPlan,
            ]
        else:
            permission_classes = [
                IsAuthenticated,
            ]

        return [
            permission()
            for permission in permission_classes
        ]