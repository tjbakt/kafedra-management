from decimal import Decimal

from django.test import TestCase

from apps.audit.models import (
    AuditEvent,
)

from apps.curriculum.models import (
    AcademicYearWorkloadNorm,
    WorkloadType,
)

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


class TeachingStreamWorkloadCalculatorTests(
    TestCase
):
    def setUp(self):
        self.user = (
            UserFactory()
        )

    def create_stream(
        self,
        *,
        workload_code,
        mode,
        base_hours,
        is_teaching_load=True,
    ):
        workload_type = (
            WorkloadTypeFactory(
                code=(
                    workload_code
                ),

                calculation_mode=(
                    mode
                ),

                is_teaching_load=(
                    is_teaching_load
                ),
            )
        )

        curriculum = (
            CurriculumFactory()
        )

        discipline = (
            CurriculumDisciplineFactory(
                curriculum=(
                    curriculum
                ),

                semester_number=1,
            )
        )

        workload = (
            CurriculumWorkloadFactory(
                curriculum_discipline=(
                    discipline
                ),

                workload_type=(
                    workload_type
                ),

                calculation_mode=(
                    mode
                ),

                base_hours=(
                    Decimal(
                        base_hours
                    )
                ),
            )
        )

        stream = (
            TeachingStreamFactory(
                curriculum=(
                    curriculum
                ),

                semester_number=1,
            )
        )

        return (
            stream,
            workload,
            workload_type,
        )

    def test_rejects_stream_without_groups(
        self,
    ):
        (
            stream,
            _,
            _,
        ) = self.create_stream(
            workload_code=(
                WorkloadType
                .Code
                .PRACTICE
            ),

            mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),

            base_hours="30.00",
        )

        calculator = (
            TeachingStreamWorkloadCalculator(
                stream
            )
        )

        with self.assertRaises(
            ValueError
        ):
            calculator.calculate(
                teaching_stream=(
                    stream
                ),

                user=self.user,
            )

    def test_lecture_creates_one_stream_row(
        self,
    ):
        (
            stream,
            _,
            _,
        ) = self.create_stream(
            workload_code=(
                WorkloadType
                .Code
                .LECTURE
            ),

            mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),

            base_hours="30.00",
        )

        TeachingStreamGroupFactory.create_batch(
            2,
            teaching_stream=(
                stream
            ),
        )

        results = (
            TeachingStreamWorkloadCalculator(
                stream
            )
            .calculate(
                teaching_stream=(
                    stream
                ),

                user=self.user,
            )
        )

        self.assertEqual(
            len(results),
            1,
        )

        result = results[0]

        self.assertIsNone(
            result.group_semester_id
        )

        self.assertEqual(
            result
            .calculation_quantity,

            Decimal("1.00"),
        )

        self.assertEqual(
            result.total_hours,

            Decimal("30.00"),
        )

        self.assertEqual(
            result.groups_count,
            2,
        )

    def test_practice_creates_row_for_each_group(
        self,
    ):
        (
            stream,
            _,
            _,
        ) = self.create_stream(
            workload_code=(
                WorkloadType
                .Code
                .PRACTICE
            ),

            mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),

            base_hours="16.00",
        )

        memberships = [
            TeachingStreamGroupFactory(
                teaching_stream=(
                    stream
                )
            ),
            TeachingStreamGroupFactory(
                teaching_stream=(
                    stream
                )
            ),
        ]

        results = (
            TeachingStreamWorkloadCalculator(
                stream
            )
            .calculate(
                teaching_stream=(
                    stream
                ),

                user=self.user,
            )
        )

        self.assertEqual(
            len(results),
            2,
        )

        expected_group_ids = {
            item
            .group_semester_id
            for item
            in memberships
        }

        actual_group_ids = {
            item
            .group_semester_id
            for item
            in results
        }

        self.assertEqual(
            actual_group_ids,
            expected_group_ids,
        )

        for result in results:
            self.assertEqual(
                result
                .calculation_quantity,

                Decimal("1.00"),
            )

            self.assertEqual(
                result.total_hours,

                Decimal("16.00"),
            )

            self.assertEqual(
                result.groups_count,
                1,
            )

    def test_laboratory_uses_subgroup_count(
        self,
    ):
        (
            stream,
            _,
            _,
        ) = self.create_stream(
            workload_code=(
                WorkloadType
                .Code
                .LABORATORY
            ),

            mode=(
                WorkloadType
                .CalculationMode
                .PER_SUBGROUP
            ),

            base_hours="14.00",
        )

        membership = (
            TeachingStreamGroupFactory(
                teaching_stream=(
                    stream
                )
            )
        )

        group_semester = (
            membership
            .group_semester
        )

        group_semester.subgroup_count = 2

        group_semester.save(
            update_fields=(
                "subgroup_count",
            )
        )

        result = (
            TeachingStreamWorkloadCalculator(
                stream
            )
            .calculate(
                teaching_stream=(
                    stream
                ),

                user=self.user,
            )[0]
        )

        self.assertEqual(
            result
            .calculation_quantity,

            Decimal("2"),
        )

        self.assertEqual(
            result.total_hours,

            Decimal("28.00"),
        )

    def test_per_student_uses_students_of_group(
        self,
    ):
        (
            stream,
            _,
            _,
        ) = self.create_stream(
            workload_code=(
                WorkloadType
                .Code
                .OTHER
            ),

            mode=(
                WorkloadType
                .CalculationMode
                .PER_STUDENT
            ),

            base_hours="0.50",
        )

        membership = (
            TeachingStreamGroupFactory(
                teaching_stream=(
                    stream
                )
            )
        )

        group_semester = (
            membership
            .group_semester
        )

        group_semester.students_count = 20

        group_semester.save(
            update_fields=(
                "students_count",
            )
        )

        result = (
            TeachingStreamWorkloadCalculator(
                stream
            )
            .calculate(
                teaching_stream=(
                    stream
                ),

                user=self.user,
            )[0]
        )

        self.assertEqual(
            result
            .calculation_quantity,

            Decimal("20"),
        )

        self.assertEqual(
            result.total_hours,

            Decimal("10.00"),
        )

    def test_weekly_practice_uses_group_weeks(
        self,
    ):
        (
            stream,
            workload,
            workload_type,
        ) = self.create_stream(
            workload_code=(
                WorkloadType
                .Code
                .QUALIFICATION_PRACTICE_SUPERVISION
            ),

            mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),

            base_hours="0.00",
        )

        membership = (
            TeachingStreamGroupFactory(
                teaching_stream=(
                    stream
                )
            )
        )

        group_semester = (
            membership
            .group_semester
        )

        group_semester.weeks_count = 5

        group_semester.save(
            update_fields=(
                "weeks_count",
            )
        )

        AcademicYearWorkloadNorm.objects.create(
            academic_year=(
                stream.academic_year
            ),

            workload_type=(
                workload_type
            ),

            coefficient=(
                Decimal("6.0000")
            ),

            is_active=True,

            created_by=self.user,

            updated_by=self.user,
        )

        result = (
            TeachingStreamWorkloadCalculator(
                stream
            )
            .calculate(
                teaching_stream=(
                    stream
                ),

                user=self.user,
            )[0]
        )

        self.assertEqual(
            result
            .curriculum_workload_id,

            workload.id,
        )

        self.assertEqual(
            result.base_hours,

            Decimal("6.0000"),
        )

        self.assertEqual(
            result
            .calculation_quantity,

            Decimal("5"),
        )

        self.assertEqual(
            result.total_hours,

            Decimal("30.0000"),
        )

    def test_non_teaching_work_is_ignored(
        self,
    ):
        (
            stream,
            _,
            _,
        ) = self.create_stream(
            workload_code=(
                WorkloadType
                .Code
                .INDEPENDENT_WORK
            ),

            mode=(
                WorkloadType
                .CalculationMode
                .FIXED
            ),

            base_hours="60.00",

            is_teaching_load=False,
        )

        TeachingStreamGroupFactory(
            teaching_stream=(
                stream
            )
        )

        calculator = (
            TeachingStreamWorkloadCalculator(
                stream
            )
        )

        with self.assertRaises(
            ValueError
        ):
            calculator.calculate(
                teaching_stream=(
                    stream
                ),

                user=self.user,
            )

        self.assertFalse(
            PlannedWorkload
            .objects
            .filter(
                teaching_stream=(
                    stream
                )
            )
            .exists()
        )

    def test_recalculation_updates_same_group_rows(
        self,
    ):
        (
            stream,
            workload,
            _,
        ) = self.create_stream(
            workload_code=(
                WorkloadType
                .Code
                .PRACTICE
            ),

            mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),

            base_hours="10.00",
        )

        membership = (
            TeachingStreamGroupFactory(
                teaching_stream=(
                    stream
                )
            )
        )

        first = (
            TeachingStreamWorkloadCalculator(
                stream
            )
            .calculate(
                teaching_stream=(
                    stream
                ),

                user=self.user,
            )[0]
        )

        first_pk = first.pk

        workload.base_hours = (
            Decimal("20.00")
        )

        workload.save(
            update_fields=(
                "base_hours",
            )
        )

        second = (
            TeachingStreamWorkloadCalculator(
                stream
            )
            .calculate(
                teaching_stream=(
                    stream
                ),

                user=self.user,
            )[0]
        )

        self.assertEqual(
            first_pk,
            second.pk,
        )

        self.assertEqual(
            second
            .group_semester_id,

            membership
            .group_semester_id,
        )

        self.assertEqual(
            second.total_hours,

            Decimal("20.00"),
        )

    def test_removed_group_row_is_archived(
        self,
    ):
        (
            stream,
            _,
            _,
        ) = self.create_stream(
            workload_code=(
                WorkloadType
                .Code
                .PRACTICE
            ),

            mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),

            base_hours="10.00",
        )

        first_membership = (
            TeachingStreamGroupFactory(
                teaching_stream=(
                    stream
                )
            )
        )

        second_membership = (
            TeachingStreamGroupFactory(
                teaching_stream=(
                    stream
                )
            )
        )

        TeachingStreamWorkloadCalculator(
            stream
        ).calculate(
            teaching_stream=(
                stream
            ),

            user=self.user,
        )

        second_group_id = (
            second_membership
            .group_semester_id
        )

        second_membership.is_active = (
            False
        )

        second_membership.save(
            update_fields=(
                "is_active",
            )
        )

        TeachingStreamWorkloadCalculator(
            stream
        ).calculate(
            teaching_stream=(
                stream
            ),

            user=self.user,
        )

        active_group_ids = set(
            PlannedWorkload
            .objects
            .filter(
                teaching_stream=(
                    stream
                )
            )
            .values_list(
                "group_semester_id",
                flat=True,
            )
        )

        self.assertIn(
            first_membership
            .group_semester_id,

            active_group_ids,
        )

        self.assertNotIn(
            second_group_id,

            active_group_ids,
        )

        archived = (
            PlannedWorkload
            .all_objects
            .get(
                teaching_stream=(
                    stream
                ),

                group_semester_id=(
                    second_group_id
                ),
            )
        )

        self.assertTrue(
            archived.is_archived
        )

        self.assertIsNotNone(
            archived.archived_at
        )

    def test_calculation_sets_stream_status(
        self,
    ):
        (
            stream,
            _,
            _,
        ) = self.create_stream(
            workload_code=(
                WorkloadType
                .Code
                .PRACTICE
            ),

            mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),

            base_hours="16.00",
        )

        TeachingStreamGroupFactory(
            teaching_stream=(
                stream
            )
        )

        TeachingStreamWorkloadCalculator(
            stream
        ).calculate(
            teaching_stream=(
                stream
            ),

            user=self.user,
        )

        stream.refresh_from_db()

        self.assertEqual(
            stream.status,

            TeachingStream
            .Status
            .CALCULATED,
        )

    def test_calculation_creates_audit_event(
        self,
    ):
        (
            stream,
            _,
            _,
        ) = self.create_stream(
            workload_code=(
                WorkloadType
                .Code
                .PRACTICE
            ),

            mode=(
                WorkloadType
                .CalculationMode
                .PER_GROUP
            ),

            base_hours="16.00",
        )

        TeachingStreamGroupFactory(
            teaching_stream=(
                stream
            )
        )

        result = (
            TeachingStreamWorkloadCalculator(
                stream
            )
            .calculate(
                teaching_stream=(
                    stream
                ),

                user=self.user,
            )[0]
        )

        self.assertTrue(
            AuditEvent.objects
            .filter(
                actor=self.user,

                action=(
                    AuditEvent
                    .Action
                    .CALCULATE
                ),

                object_id=(
                    str(result.pk)
                ),
            )
            .exists()
        )