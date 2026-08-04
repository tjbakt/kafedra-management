import factory
from django.contrib.contenttypes.models import (
    ContentType,
)

from apps.audit.models import AuditEvent
from tests.factories.accounts import UserFactory
from tests.factories.organizations import (
    DepartmentFactory,
)


class AuditEventFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = AuditEvent

    actor = factory.SubFactory(
        UserFactory
    )

    content_type = factory.LazyFunction(
        lambda: (
            ContentType.objects.get_for_model(
                DepartmentFactory._meta.model
            )
        )
    )
    object_id = factory.Sequence(
        lambda number: str(number + 1)
    )
    object_repr = factory.Sequence(
        lambda number: (
            f"Тестовый объект {number}"
        )
    )

    action = AuditEvent.Action.UPDATE
    action_label = "Изменение тестового объекта"

    old_values = factory.LazyFunction(dict)
    new_values = factory.LazyFunction(dict)
    changed_fields = factory.LazyFunction(list)
    metadata = factory.LazyFunction(dict)

    reason = ""

    actor_username = factory.LazyAttribute(
        lambda obj: obj.actor.username
    )
    actor_full_name = factory.LazyAttribute(
        lambda obj: (
            obj.actor.get_full_name()
            or obj.actor.username
        )
    )

    ip_address = "127.0.0.1"
    user_agent = "Test client"
    request_method = "PATCH"
    request_path = "/api/v1/test/"

    university_id = None
    faculty_id = None
    department_id = None
    staff_member_id = None
    academic_year_id = None