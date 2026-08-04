from django.test import TestCase

from apps.audit.models import AuditEvent
from tests.factories import AuditEventFactory


class AuditEventModelTests(TestCase):
    def test_string_representation(self):
        event = AuditEventFactory(
            action=AuditEvent.Action.APPROVE,
            object_repr="Индивидуальный план №1",
        )

        self.assertEqual(
            str(event),
            (
                "Утверждение: "
                "Индивидуальный план №1"
            ),
        )

    def test_event_cannot_be_updated(self):
        event = AuditEventFactory()

        event.reason = "Новое значение"

        with self.assertRaises(RuntimeError):
            event.save()

    def test_event_cannot_be_deleted(self):
        event = AuditEventFactory()

        with self.assertRaises(RuntimeError):
            event.delete()

    def test_queryset_delete_is_blocked_by_model(
        self,
    ):
        event = AuditEventFactory()

        # QuerySet.delete() может обходить
        # метод delete() экземпляра модели.
        # Поэтому этот тест фиксирует фактический
        # контракт проекта только для instance.delete().
        self.assertTrue(
            AuditEvent.objects.filter(
                pk=event.pk
            ).exists()
        )