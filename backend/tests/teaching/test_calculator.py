from decimal import Decimal

from django.test import TestCase

from apps.audit.models import AuditEvent
from apps.curriculum.models import WorkloadType
from apps.teaching.models import (
    PlannedWorkload,
    TeachingStream,
)
from apps.teaching.services.workload_calculator import (
    TeachingStreamWorkloadCalculator,
)
from tests.factories import (
    CurriculumDisciplineFactory,
    CurriculumFactory,
    CurriculumWorkloadFactory,
    TeachingStreamFactory,
    TeachingStreamGroupFactory,
    UserFactory,
    WorkloadTypeFactory,
)


class TeachingStreamWorkloadCalculatorTests(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def create_stream(self, *, mode, base_hours):
        workload_type = WorkloadTypeFactory(
            calculation_mode=mode,
        )
        curriculum = CurriculumFactory()

        discipline = CurriculumDisciplineFactory(
            curriculum=curriculum,
            semester_number=1,
        )
        CurriculumWorkloadFactory(
            curriculum_discipline=discipline,
            workload_type=workload_type,
            calculation_mode=mode,
            base_hours=Decimal(base_hours),
        )

        return TeachingStreamFactory(
            curriculum=curriculum,
            semester_number=1,
        )

    def test_rejects_stream_without_groups(self):
        stream = self.create_stream(
            mode=WorkloadType.CalculationMode.PER_GROUP,
            base_hours="30.00",
        )

        calculator = TeachingStreamWorkloadCalculator(stream)

        with self.assertRaises(ValueError):
            calculator.calculate(
                teaching_stream=stream,
                user=self.user,
            )

    def test_per_group_calculation(self):
        stream = self.create_stream(
            mode=WorkloadType.CalculationMode.PER_GROUP,
            base_hours="30.00",
        )

        TeachingStreamGroupFactory.create_batch(
            2,
            teaching_stream=stream,
        )

        results = TeachingStreamWorkloadCalculator(
            stream
        ).calculate(
            teaching_stream=stream,
            user=self.user,
        )

        self.assertEqual(len(results), 1)
        result = results[0]

        self.assertEqual(
            result.calculation_quantity,
            Decimal("2"),
        )
        self.assertEqual(
            result.total_hours,
            Decimal("60.00"),
        )
        self.assertEqual(result.groups_count, 2)

        stream.refresh_from_db()
        self.assertEqual(
            stream.status,
            TeachingStream.Status.CALCULATED,
        )

    def test_per_student_calculation(self):
        stream = self.create_stream(
            mode=WorkloadType.CalculationMode.PER_STUDENT,
            base_hours="0.50",
        )

        membership = TeachingStreamGroupFactory(
            teaching_stream=stream,
        )
        membership.group_semester.students_count = 20
        membership.group_semester.save(
            update_fields=("students_count",)
        )

        results = TeachingStreamWorkloadCalculator(
            stream
        ).calculate(
            teaching_stream=stream,
            user=self.user,
        )

        self.assertEqual(len(results), 1)
        result = results[0]

        self.assertEqual(
            result.calculation_quantity,
            Decimal("20"),
        )
        self.assertEqual(
            result.total_hours,
            Decimal("10.00"),
        )

    def test_recalculation_updates_record(self):
        stream = self.create_stream(
            mode=WorkloadType.CalculationMode.PER_GROUP,
            base_hours="10.00",
        )

        TeachingStreamGroupFactory(
            teaching_stream=stream,
        )

        first_results = TeachingStreamWorkloadCalculator(
            stream
        ).calculate(
            teaching_stream=stream,
            user=self.user,
        )
        first = first_results[0]

        workload = first.curriculum_workload
        workload.base_hours = Decimal("20.00")
        workload.save(update_fields=("base_hours",))

        second_results = TeachingStreamWorkloadCalculator(
            stream
        ).calculate(
            teaching_stream=stream,
            user=self.user,
        )
        second = second_results[0]

        self.assertEqual(first.pk, second.pk)
        self.assertEqual(
            second.total_hours,
            Decimal("20.00"),
        )

    def test_calculation_creates_audit_event(self):
        stream = self.create_stream(
            mode=WorkloadType.CalculationMode.FIXED,
            base_hours="24.00",
        )

        TeachingStreamGroupFactory(
            teaching_stream=stream,
        )

        results = TeachingStreamWorkloadCalculator(
            stream
        ).calculate(
            teaching_stream=stream,
            user=self.user,
        )
        result = results[0]

        self.assertTrue(
            AuditEvent.objects.filter(
                actor=self.user,
                action=AuditEvent.Action.CALCULATE,
                object_id=str(result.pk),
            ).exists()
        )