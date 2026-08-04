from django.test import TestCase

from apps.audit.api.serializers import (
    AuditEventSerializer,
)
from tests.factories import AuditEventFactory


class AuditEventSerializerTests(TestCase):
    def test_output_fields(self):
        event = AuditEventFactory()

        serializer = AuditEventSerializer(
            event
        )

        self.assertEqual(
            serializer.data["object_id"],
            event.object_id,
        )
        self.assertEqual(
            serializer.data["action"],
            event.action,
        )
        self.assertEqual(
            serializer.data["actor"],
            event.actor_id,
        )
        self.assertIn(
            "action_name",
            serializer.data,
        )
        self.assertIn(
            "app_label",
            serializer.data,
        )
        self.assertIn(
            "model",
            serializer.data,
        )

    def test_all_fields_are_read_only(self):
        event = AuditEventFactory()

        serializer = AuditEventSerializer(
            event,
            data={
                "reason": "Изменение",
                "action": "delete",
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        # save() вызывать нельзя:
        # модель аудита неизменяема.
        self.assertEqual(
            serializer.validated_data,
            {},
        )