from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model

from apps.audit.middleware import get_current_request
from apps.audit.models import AuditEvent


class AuditService:
    """
    Централизованное создание бизнес-событий аудита.
    """

    SENSITIVE_FIELDS = {
        "password",
        "token",
        "access",
        "refresh",
        "secret",
        "api_key",
    }

    @classmethod
    def serialize_value(cls, value):
        if isinstance(value, Model):
            return value.pk

        if isinstance(value, Decimal):
            return str(value)

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if isinstance(value, UUID):
            return str(value)

        if isinstance(value, (list, tuple, set)):
            return [
                cls.serialize_value(item)
                for item in value
            ]

        if isinstance(value, dict):
            return {
                str(key): cls.serialize_value(item)
                for key, item in value.items()
            }

        return value

    @classmethod
    def clean_values(cls, values):
        if not values:
            return {}

        result = {}

        for field_name, value in values.items():
            lowered = field_name.lower()

            if any(
                sensitive in lowered
                for sensitive in cls.SENSITIVE_FIELDS
            ):
                result[field_name] = "***"
            else:
                result[field_name] = (
                    cls.serialize_value(value)
                )

        return result

    @staticmethod
    def get_client_ip(request):
        if not request:
            return None

        forwarded_for = request.META.get(
            "HTTP_X_FORWARDED_FOR"
        )

        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        return request.META.get("REMOTE_ADDR")

    @staticmethod
    def get_actor_data(actor):
        if not actor or not actor.is_authenticated:
            return {
                "actor": None,
                "actor_username": "",
                "actor_full_name": "",
            }

        full_name = ""

        if hasattr(actor, "get_full_name"):
            full_name = actor.get_full_name() or ""

        return {
            "actor": actor,
            "actor_username": getattr(
                actor,
                "username",
                "",
            ),
            "actor_full_name": full_name,
        }

    @staticmethod
    def infer_context(instance):
        """
        Определяет организационный контекст объекта.

        Возвращает только простые ID, поэтому журнал не зависит
        от последующего удаления или изменения связанных объектов.
        """

        context = {
            "university_id": None,
            "faculty_id": None,
            "department_id": None,
            "staff_member_id": None,
            "academic_year_id": None,
        }

        if instance is None:
            return context

        if hasattr(instance, "academic_year_id"):
            context["academic_year_id"] = getattr(
                instance,
                "academic_year_id",
                None,
            )

        if hasattr(instance, "staff_member_id"):
            context["staff_member_id"] = getattr(
                instance,
                "staff_member_id",
                None,
            )

        if hasattr(instance, "department_id"):
            context["department_id"] = getattr(
                instance,
                "department_id",
                None,
            )

        staff_employment = getattr(
            instance,
            "staff_employment",
            None,
        )

        if staff_employment:
            context["staff_member_id"] = (
                staff_employment.staff_member_id
            )
            context["department_id"] = (
                staff_employment.department_id
            )

        planned_workload = getattr(
            instance,
            "planned_workload",
            None,
        )

        if planned_workload:
            context["academic_year_id"] = (
                planned_workload.academic_year_id
            )
            context["department_id"] = (
                planned_workload.teaching_department_id
            )

        individual_plan = getattr(
            instance,
            "individual_plan",
            None,
        )

        if individual_plan:
            context["academic_year_id"] = (
                individual_plan.academic_year_id
            )
            context["staff_member_id"] = (
                individual_plan
                .staff_employment
                .staff_member_id
            )
            context["department_id"] = (
                individual_plan
                .staff_employment
                .department_id
            )

        department = getattr(
            instance,
            "department",
            None,
        )

        if department and hasattr(department, "faculty_id"):
            context["faculty_id"] = department.faculty_id

            faculty = getattr(
                department,
                "faculty",
                None,
            )

            if faculty:
                context["university_id"] = (
                    faculty.university_id
                )

        if context["department_id"] and not context["faculty_id"]:
            department_object = None

            if staff_employment:
                department_object = (
                    staff_employment.department
                )
            elif planned_workload:
                department_object = (
                    planned_workload.teaching_department
                )

            if department_object:
                context["faculty_id"] = (
                    department_object.faculty_id
                )
                context["university_id"] = (
                    department_object
                    .faculty
                    .university_id
                )

        faculty = getattr(instance, "faculty", None)

        if faculty:
            context["faculty_id"] = faculty.pk
            context["university_id"] = (
                faculty.university_id
            )

        university = getattr(
            instance,
            "university",
            None,
        )

        if university:
            context["university_id"] = university.pk

        return context

    @classmethod
    def log(
        cls,
        *,
        instance,
        action,
        actor=None,
        action_label="",
        old_values=None,
        new_values=None,
        changed_fields=None,
        reason="",
        metadata=None,
        request=None,
        context=None,
    ):
        request = request or get_current_request()

        if actor is None and request:
            actor = getattr(request, "user", None)

        actor_data = cls.get_actor_data(actor)

        inferred_context = cls.infer_context(instance)

        if context:
            inferred_context.update(
                {
                    key: value
                    for key, value in context.items()
                    if value is not None
                }
            )

        content_type = ContentType.objects.get_for_model(
            instance,
            for_concrete_model=False,
        )

        return AuditEvent.objects.create(
            content_type=content_type,
            object_id=str(instance.pk),
            object_repr=str(instance)[:1000],
            action=action,
            action_label=action_label,
            old_values=cls.clean_values(old_values),
            new_values=cls.clean_values(new_values),
            changed_fields=list(changed_fields or []),
            reason=reason or "",
            metadata=cls.clean_values(metadata),
            ip_address=cls.get_client_ip(request),
            user_agent=(
                request.META.get(
                    "HTTP_USER_AGENT",
                    "",
                )[:5000]
                if request
                else ""
            ),
            request_method=(
                request.method
                if request
                else ""
            ),
            request_path=(
                request.path[:2000]
                if request
                else ""
            ),
            **actor_data,
            **inferred_context,
        )

    @classmethod
    def log_status_change(
        cls,
        *,
        instance,
        old_status,
        new_status,
        actor=None,
        reason="",
        action=None,
        action_label="",
        metadata=None,
    ):
        return cls.log(
            instance=instance,
            action=action or AuditEvent.Action.STATUS_CHANGE,
            actor=actor,
            action_label=action_label,
            old_values={
                "status": old_status,
            },
            new_values={
                "status": new_status,
            },
            changed_fields=[
                "status",
            ],
            reason=reason,
            metadata=metadata,
        )

    @classmethod
    def model_snapshot(
        cls,
        instance,
        field_names,
    ):
        result = {}

        for field_name in field_names:
            value = getattr(instance, field_name)

            if hasattr(value, "pk"):
                value = value.pk

            result[field_name] = cls.serialize_value(value)

        return result