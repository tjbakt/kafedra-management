from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.individual_plan.models import (
    IndividualPlan,
    IndividualPlanItem,
    IndividualPlanSection,
    IndividualPlanTeachingWorkload,
)
from apps.workload.models import WorkloadDistribution

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


class IndividualPlanService:
    @staticmethod
    @transaction.atomic
    def create_plan(
        *,
        staff_employment,
        academic_year,
        user=None,
    ):
        plan, created = IndividualPlan.all_objects.get_or_create(
            staff_employment=staff_employment,
            academic_year=academic_year,
            is_archived=False,
            defaults={
                "status": IndividualPlan.Status.DRAFT,
                "created_by": user,
                "updated_by": user,
            },
        )

        if created:
            AuditService.log(
                instance=plan,
                action=AuditEvent.Action.CREATE,
                actor=user,
                action_label="Создан индивидуальный план",
                new_values={
                    "staff_employment": plan.staff_employment_id,
                    "academic_year": plan.academic_year_id,
                    "status": plan.status,
                },
                changed_fields=[
                    "staff_employment",
                    "academic_year",
                    "status",
                ],
            )

        return plan, created

    @staticmethod
    @transaction.atomic
    def import_teaching_workload(*, plan, user=None):
        if plan.status not in (
            IndividualPlan.Status.DRAFT,
            IndividualPlan.Status.RETURNED,
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Импорт нагрузки разрешён только "
                        "для черновика или возвращённого плана."
                    )
                }
            )

        teaching_section = IndividualPlanSection.objects.filter(
            code=IndividualPlanSection.Code.TEACHING,
            is_active=True,
        ).first()

        if not teaching_section:
            raise ValidationError(
                {
                    "detail": (
                        "Раздел «Учебная работа» не настроен."
                    )
                }
            )

        distributions = (
            WorkloadDistribution.objects
            .select_related(
                "planned_workload",
                "planned_workload__academic_semester",
                "planned_workload__teaching_stream",
                "planned_workload__teaching_stream__"
                "curriculum_discipline",
                "planned_workload__teaching_stream__"
                "curriculum_discipline__discipline",
                "planned_workload__curriculum_workload",
                "planned_workload__curriculum_workload__"
                "workload_type",
            )
            .filter(
                staff_employment=plan.staff_employment,
                planned_workload__academic_year=plan.academic_year,
                status=WorkloadDistribution.Status.APPROVED,
            )
        )

        created_count = 0
        updated_count = 0

        for distribution in distributions:
            planned = distribution.planned_workload
            discipline = (
                planned.teaching_stream
                .curriculum_discipline.discipline
            )
            workload_type = (
                planned.curriculum_workload.workload_type
            )

            title = (
                f"{discipline.name_ru} — "
                f"{workload_type.name_ru}"
            )

            link = (
                IndividualPlanTeachingWorkload.all_objects
                .filter(
                    workload_distribution=distribution,
                    is_archived=False,
                )
                .select_related("plan_item")
                .first()
            )

            if link:
                item = link.plan_item
                item.planned_hours = distribution.allocated_hours
                item.academic_semester = (
                    planned.academic_semester
                )
                item.title = title
                item.updated_by = user
                item.save(
                    update_fields=(
                        "planned_hours",
                        "academic_semester",
                        "title",
                        "updated_by",
                        "updated_at",
                    )
                )

                link.imported_hours = (
                    distribution.allocated_hours
                )
                link.updated_by = user
                link.save(
                    update_fields=(
                        "imported_hours",
                        "updated_by",
                        "updated_at",
                    )
                )
                updated_count += 1
                continue

            item = IndividualPlanItem.objects.create(
                individual_plan=plan,
                section=teaching_section,
                academic_semester=planned.academic_semester,
                title=title,
                description=(
                    f"Поток: "
                    f"{planned.teaching_stream.code}"
                ),
                planned_hours=distribution.allocated_hours,
                status=IndividualPlanItem.Status.PLANNED,
                created_by=user,
                updated_by=user,
            )

            IndividualPlanTeachingWorkload.objects.create(
                plan_item=item,
                workload_distribution=distribution,
                imported_hours=distribution.allocated_hours,
                created_by=user,
                updated_by=user,
            )

            created_count += 1

        AuditService.log(
            instance=plan,
            action=AuditEvent.Action.IMPORT,
            actor=user,
            action_label=(
                "Учебная нагрузка импортирована "
                "в индивидуальный план"
            ),
            new_values={
                "created_count": created_count,
                "updated_count": updated_count,
                "total_count": distributions.count(),
            },
            metadata={
                "source_model": "workload.WorkloadDistribution",
            },
        )

        return {
            "created_count": created_count,
            "updated_count": updated_count,
            "total_count": distributions.count(),
        }


    @staticmethod
    @transaction.atomic
    def submit_plan(*, plan, user=None):
        if plan.status not in (
            IndividualPlan.Status.DRAFT,
            IndividualPlan.Status.RETURNED,
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Этот план нельзя отправить на рассмотрение."
                    )
                }
            )

        if not plan.items.filter(
            is_archived=False
        ).exists():
            raise ValidationError(
                {
                    "detail": (
                        "Нельзя отправить пустой индивидуальный план."
                    )
                }
            )

        plan.status = IndividualPlan.Status.SUBMITTED
        plan.submitted_at = timezone.now()
        plan.updated_by = user

        old_status = plan.status

        plan.save(
            update_fields=(
                "status",
                "submitted_at",
                "updated_by",
                "updated_at",
            )
        )

        AuditService.log_status_change(
            instance=plan,
            old_status=old_status,
            new_status=plan.status,
            actor=user,
            action=AuditEvent.Action.SUBMIT,
            action_label="Индивидуальный план отправлен на рассмотрение",
            metadata={
                "submitted_at": plan.submitted_at,
            },
        )

        department_id = plan.staff_employment.department_id

        department_heads = AccessService.users_with_role(
            role_code=SystemRole.Code.DEPARTMENT_HEAD,
            department_id=department_id,
        )

        for department_head in department_heads:
            NotificationService.create_task(
                assignee=department_head,
                task_type=(
                    UserTask.Type.APPROVE_INDIVIDUAL_PLAN
                ),
                title="Утвердить индивидуальный план",
                description=(
                    f"Преподаватель {plan.teacher_name} "
                    f"отправил индивидуальный план "
                    f"за {plan.academic_year} учебный год."
                ),
                priority=UserTask.Priority.HIGH,
                instance=plan,
                action_url=(
                    f"/individual-plans/{plan.pk}/review"
                ),
                created_by=user,
                deduplication_key=(
                    f"approve-individual-plan-{plan.pk}"
                ),
                metadata={
                    "staff_member_id": (
                        plan.staff_employment.staff_member_id
                    ),
                    "department_id": department_id,
                    "academic_year_id": plan.academic_year_id,
                },
            )

        NotificationService.complete_tasks_for_object(
            instance=plan,
            task_types=(
                UserTask.Type.UPDATE_PLAN,
            ),
            completion_comment=(
                "Исправленный план повторно отправлен."
            ),
        )

        return plan

    @staticmethod
    @transaction.atomic
    def approve_plan(*, plan, user):
        if plan.status != IndividualPlan.Status.SUBMITTED:
            raise ValidationError(
                {
                    "detail": (
                        "Утвердить можно только план, "
                        "отправленный на рассмотрение."
                    )
                }
            )

        plan.status = IndividualPlan.Status.APPROVED
        plan.approved_at = timezone.now()
        plan.approved_by = user
        plan.updated_by = user

        old_status = plan.status

        plan.save(
            update_fields=(
                "status",
                "approved_at",
                "approved_by",
                "updated_by",
                "updated_at",
            )
        )

        AuditService.log_status_change(
            instance=plan,
            old_status=old_status,
            new_status=plan.status,
            actor=user,
            action=AuditEvent.Action.APPROVE,
            action_label="Индивидуальный план утверждён",
            metadata={
                "approved_at": plan.approved_at,
                "approved_by": plan.approved_by_id,
            },
        )

        NotificationService.complete_tasks_for_object(
            instance=plan,
            task_types=(
                UserTask.Type.APPROVE_INDIVIDUAL_PLAN,
                UserTask.Type.REVIEW_INDIVIDUAL_PLAN,
            ),
            completion_comment=(
                "Индивидуальный план утверждён."
            ),
        )

        teacher_user = plan.staff_employment.staff_member.user

        if teacher_user:
            NotificationService.notify(
                recipient=teacher_user,
                title="Индивидуальный план утверждён",
                message=(
                    f"Ваш индивидуальный план за "
                    f"{plan.academic_year} учебный год утверждён."
                ),
                notification_type=Notification.Type.SUCCESS,
                instance=plan,
                action_url=f"/individual-plans/{plan.pk}",
            )

        return plan

    @staticmethod
    @transaction.atomic
    def return_plan(*, plan, reviewer_notes, user):
        if plan.status != IndividualPlan.Status.SUBMITTED:
            raise ValidationError(
                {
                    "detail": (
                        "Вернуть можно только план, "
                        "отправленный на рассмотрение."
                    )
                }
            )

        plan.status = IndividualPlan.Status.RETURNED
        plan.reviewer_notes = reviewer_notes
        plan.updated_by = user

        old_status = plan.status

        plan.save(
            update_fields=(
                "status",
                "reviewer_notes",
                "updated_by",
                "updated_at",
            )
        )

        AuditService.log_status_change(
            instance=plan,
            old_status=old_status,
            new_status=plan.status,
            actor=user,
            action=AuditEvent.Action.RETURN,
            action_label="Индивидуальный план возвращён на доработку",
            reason=reviewer_notes,
        )

        NotificationService.complete_tasks_for_object(
            instance=plan,
            task_types=(
                UserTask.Type.APPROVE_INDIVIDUAL_PLAN,
                UserTask.Type.REVIEW_INDIVIDUAL_PLAN,
            ),
            completion_comment=(
                "План возвращён преподавателю на доработку."
            ),
        )

        teacher_user = plan.staff_employment.staff_member.user

        if teacher_user:
            NotificationService.create_task(
                assignee=teacher_user,
                task_type=UserTask.Type.UPDATE_PLAN,
                title="Доработать индивидуальный план",
                description=(
                    f"Индивидуальный план возвращён на доработку. "
                    f"Комментарий: {reviewer_notes}"
                ),
                priority=UserTask.Priority.HIGH,
                instance=plan,
                action_url=f"/individual-plans/{plan.pk}/edit",
                created_by=user,
                deduplication_key=(
                    f"update-individual-plan-{plan.pk}"
                ),
                metadata={
                    "reviewer_notes": reviewer_notes,
                },
            )

        return plan