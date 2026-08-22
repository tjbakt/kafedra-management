from rest_framework import serializers
from django.utils.translation import get_language
from drf_spectacular.utils import extend_schema_field

from apps.common.api.serializers import AuditFieldsSerializer
from apps.teaching.models import (
    GroupCurriculumAssignment,
    GroupSemester,
    PlannedWorkload,
    TeachingStream,
    TeachingStreamGroup,
)
from apps.academics.models import (
    AcademicSemester,
    AcademicYear,
)
from apps.curriculum.models import (
    Curriculum,
)

class LocalizedNameMixin:
    def get_localized_name(self, obj) -> str:
        request = self.context.get("request")

        if (
            request
            and request.user
            and request.user.is_authenticated
        ):
            language = request.user.interface_language
        else:
            language = (get_language() or "ru")[:2]

        if language == "uz":
            return obj.name_uz or obj.name_ru

        return obj.name_ru or obj.name_uz

class GroupCurriculumAssignmentSerializer(
    LocalizedNameMixin,
    AuditFieldsSerializer,
):
    student_group_code = serializers.CharField(
        source="student_group.code",
        read_only=True,
    )
    curriculum_code = serializers.CharField(
        source="curriculum.code",
        read_only=True,
    )
    study_program_name = serializers.SerializerMethodField()
    study_form_name = serializers.SerializerMethodField()
    start_academic_year_name = serializers.CharField(
        source="start_academic_year.name",
        read_only=True,
    )
    end_academic_year_name = serializers.CharField(
        source="end_academic_year.name",
        read_only=True,
        allow_null=True,
    )

    @extend_schema_field(serializers.CharField())
    def get_study_program_name(self, obj) -> str:
        return self.get_localized_name(
            obj.curriculum.study_program
        )

    @extend_schema_field(serializers.CharField())
    def get_study_form_name(self, obj) -> str:
        return self.get_localized_name(
            obj.curriculum.study_form
        )

    class Meta:
        model = GroupCurriculumAssignment
        fields = (
            "id",
            "student_group",
            "student_group_code",
            "curriculum",
            "curriculum_code",
            "study_program_name",
            "study_form_name",
            "start_academic_year",
            "start_academic_year_name",
            "end_academic_year",
            "end_academic_year_name",
            "is_primary",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "is_archived",
            "archived_at",
            "archived_by",
            "archived_by_name",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

    def validate(self, attrs):
        instance = self.instance

        student_group = attrs.get(
            "student_group",
            getattr(instance, "student_group", None),
        )
        curriculum = attrs.get(
            "curriculum",
            getattr(instance, "curriculum", None),
        )

        if student_group and curriculum:
            if (
                student_group.study_program_id
                != curriculum.study_program_id
            ):
                raise serializers.ValidationError(
                    {
                        "curriculum": (
                            "Направление учебного плана не совпадает "
                            "с направлением группы."
                        )
                    }
                )

            if (
                student_group.study_form_id
                != curriculum.study_form_id
            ):
                raise serializers.ValidationError(
                    {
                        "curriculum": (
                            "Форма обучения учебного плана "
                            "не совпадает с формой группы."
                        )
                    }
                )

        start_academic_year = attrs.get(
            "start_academic_year",
            getattr(
                instance,
                "start_academic_year",
                None,
            ),
        )
        end_academic_year = attrs.get(
            "end_academic_year",
            getattr(
                instance,
                "end_academic_year",
                None,
            ),
        )

        if (
            start_academic_year
            and end_academic_year
            and end_academic_year.start_year
            < start_academic_year.start_year
        ):
            raise serializers.ValidationError(
                {
                    "end_academic_year": (
                        "Учебный год окончания не может "
                        "быть раньше учебного года начала."
                    )
                }
            )
        return attrs

class GroupSemesterSerializer(AuditFieldsSerializer):
    student_group = serializers.IntegerField(
        source="group_curriculum.student_group_id",
        read_only=True,
    )
    student_group_code = serializers.CharField(
        source="group_curriculum.student_group.code",
        read_only=True,
    )
    curriculum = serializers.IntegerField(
        source="group_curriculum.curriculum_id",
        read_only=True,
    )
    curriculum_code = serializers.CharField(
        source="group_curriculum.curriculum.code",
        read_only=True,
    )
    academic_year_name = serializers.CharField(
        source="academic_year.name",
        read_only=True,
    )
    academic_semester_name = serializers.CharField(
        source="academic_semester.get_season_display",
        read_only=True,
    )
    season = serializers.CharField(read_only=True)
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = GroupSemester
        fields = (
            "id",
            "group_curriculum",
            "student_group",
            "student_group_code",
            "curriculum",
            "curriculum_code",
            "academic_year",
            "academic_year_name",
            "academic_semester",
            "academic_semester_name",
            "semester_number",
            "season",
            "students_count",
            "subgroup_count",
            "status",
            "status_name",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "is_archived",
            "archived_at",
            "archived_by",
            "archived_by_name",
        )
        read_only_fields = (
            "id",
            "student_group",
            "curriculum",
            "season",
            "academic_semester",
            "academic_semester_name",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

    def validate(self, attrs):
        instance = self.instance

        academic_year = attrs.get(
            "academic_year",
            getattr(instance, "academic_year", None),
        )
        academic_semester = attrs.get(
            "academic_semester",
            getattr(instance, "academic_semester", None),
        )
        group_curriculum = attrs.get(
            "group_curriculum",
            getattr(instance, "group_curriculum", None),
        )
        semester_number = attrs.get(
            "semester_number",
            getattr(instance, "semester_number", None),
        )

        if (
            academic_year
            and academic_semester
            and academic_semester.academic_year_id
            != academic_year.id
        ):
            raise serializers.ValidationError(
                {
                    "academic_semester": (
                        "Семестр не относится к выбранному "
                        "учебному году."
                    )
                }
            )

        if academic_semester and semester_number:
            expected_season = (
                "autumn"
                if semester_number % 2
                else "spring"
            )

            if academic_semester.season != expected_season:
                raise serializers.ValidationError(
                    {
                        "academic_semester": (
                            "Нечётный семестр должен быть осенним, "
                            "чётный — весенним."
                        )
                    }
                )

        if group_curriculum and semester_number:
            semesters_count = (
                group_curriculum.curriculum.semesters_count
            )

            if (
                semesters_count
                and semester_number > semesters_count
            ):
                raise serializers.ValidationError(
                    {
                        "semester_number": (
                            "Номер семестра превышает длительность обучения."
                        )
                    }
                )

        allowed = self.allowed_semester_numbers(
            group_curriculum,
            academic_year,
        )
        if (
                semester_number
                not in allowed
        ):
            raise serializers.ValidationError(
                {
                    "semester_number": (
                            "Для выбранного учебного года "
                            "доступны семестры: "
                            + ", ".join(
                        map(str, allowed)
                    )
                    )
                }
            )

        return attrs

    def resolve_academic_semester(
            self,
            *,
            academic_year,
            semester_number,
    ):
        season = (
            AcademicSemester.Season.AUTUMN
            if semester_number % 2 == 1
            else AcademicSemester.Season.SPRING
        )

        try:
            return (
                AcademicSemester.objects.get(
                    academic_year=academic_year,
                    season=season,
                    is_active=True,
                    is_archived=False,
                )
            )
        except AcademicSemester.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "semester_number": (
                        "Для выбранного учебного года "
                        "не создан соответствующий "
                        "академический семестр."
                    )
                }
            )

    def allowed_semester_numbers(
            self,
            group_curriculum,
            academic_year,
    ):
        if (
                not group_curriculum
                or not academic_year
        ):
            return []

        year_index = (
                academic_year.start_year
                -
                group_curriculum
                .start_academic_year
                .start_year
        )

        if year_index < 0:
            return []

        first = (
                year_index * 2 + 1
        )

        result = [
            first,
            first + 1,
        ]

        semesters_count = (
            group_curriculum
            .curriculum
            .semesters_count
        )

        return [
            value
            for value in result
            if (
                    semesters_count is None
                    or value <= semesters_count
            )
        ]

    def create(
            self,
            validated_data,
    ):
        academic_year = (
            validated_data[
                "academic_year"
            ]
        )

        semester_number = (
            validated_data[
                "semester_number"
            ]
        )

        validated_data[
            "academic_semester"
        ] = (
            self.resolve_academic_semester(
                academic_year=academic_year,
                semester_number=semester_number,
            )
        )

        return super().create(
            validated_data
        )

    def update(
            self,
            instance,
            validated_data,
    ):
        academic_year = (
            validated_data.get(
                "academic_year",
                instance.academic_year,
            )
        )

        semester_number = (
            validated_data.get(
                "semester_number",
                instance.semester_number,
            )
        )

        validated_data[
            "academic_semester"
        ] = (
            self.resolve_academic_semester(
                academic_year=academic_year,
                semester_number=semester_number,
            )
        )

        return super().update(
            instance,
            validated_data,
        )

class TeachingStreamGroupSerializer(
    AuditFieldsSerializer
):
    student_group = serializers.IntegerField(
        source=(
            "group_semester.group_curriculum.student_group_id"
        ),
        read_only=True,
    )
    student_group_code = serializers.CharField(
        source=(
            "group_semester.group_curriculum."
            "student_group.code"
        ),
        read_only=True,
    )
    students_count = serializers.IntegerField(
        source="group_semester.students_count",
        read_only=True,
    )
    subgroup_count = serializers.IntegerField(
        source="group_semester.subgroup_count",
        read_only=True,
    )

    class Meta:
        model = TeachingStreamGroup
        fields = (
            "id",
            "teaching_stream",
            "group_semester",
            "student_group",
            "student_group_code",
            "students_count",
            "subgroup_count",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "is_archived",
            "archived_at",
            "archived_by",
            "archived_by_name",
        )
        read_only_fields = (
            "id",
            "student_group",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

    def validate(self, attrs):
        stream = attrs.get(
            "teaching_stream",
            getattr(self.instance, "teaching_stream", None),
        )
        group_semester = attrs.get(
            "group_semester",
            getattr(self.instance, "group_semester", None),
        )

        if not stream or not group_semester:
            return attrs

        if group_semester.academic_year_id != stream.academic_year_id:
            raise serializers.ValidationError(
                {
                    "group_semester": (
                        "Учебный год группы не совпадает "
                        "с учебным годом потока."
                    )
                }
            )

        if (
            group_semester.academic_semester_id
            != stream.academic_semester_id
        ):
            raise serializers.ValidationError(
                {
                    "group_semester": (
                        "Семестр группы не совпадает "
                        "с семестром потока."
                    )
                }
            )

        if (
            group_semester.curriculum.id
            != stream.curriculum_id
        ):
            raise serializers.ValidationError(
                {
                    "group_semester": (
                        "Учебный план группы "
                        "не совпадает с учебным "
                        "планом потока."
                    )
                }
            )

        if (
            group_semester.semester_number
            != stream.semester_number
        ):
            raise serializers.ValidationError(
                {
                    "group_semester": (
                        "Номер семестра группы "
                        "не совпадает с номером "
                        "семестра потока."
                    )
                }
            )

        return attrs

class TeachingStreamSerializer(
    LocalizedNameMixin,
    AuditFieldsSerializer,
):
    academic_year_name = serializers.CharField(
        source="academic_year.name",
        read_only=True,
    )

    academic_semester_name = serializers.CharField(
        source="academic_semester.get_season_display",
        read_only=True,
    )

    curriculum_code = serializers.CharField(
        source="curriculum.code",
        read_only=True,
    )

    study_program_name = serializers.SerializerMethodField()

    study_form_name = serializers.SerializerMethodField()

    groups_count = serializers.IntegerField(
        read_only=True,
    )

    students_count = serializers.IntegerField(
        read_only=True,
    )

    subgroups_count = serializers.IntegerField(
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    stream_groups = TeachingStreamGroupSerializer(
        many=True,
        read_only=True,
    )

    planned_workloads_count = serializers.SerializerMethodField()

    total_planned_hours = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_study_program_name(
        self,
        obj,
    ) -> str:
        return self.get_localized_name(
            obj.curriculum.study_program
        )

    @extend_schema_field(serializers.CharField())
    def get_study_form_name(
        self,
        obj,
    ) -> str:
        return self.get_localized_name(
            obj.curriculum.study_form
        )

    @extend_schema_field(serializers.IntegerField())
    def get_planned_workloads_count(
        self,
        obj,
    ) -> int:
        return obj.planned_workloads.filter(
            is_archived=False,
        ).count()

    @extend_schema_field(
        serializers.DecimalField(
            max_digits=14,
            decimal_places=2,
        )
    )
    def get_total_planned_hours(
        self,
        obj,
    ):
        from django.db.models import Sum

        return (
            obj.planned_workloads
            .filter(
                is_archived=False,
            )
            .aggregate(
                total=Sum(
                    "total_hours"
                )
            )["total"]
            or 0
        )

    class Meta:
        model = TeachingStream

        fields = (
            "id",

            "academic_year",
            "academic_year_name",

            "academic_semester",
            "academic_semester_name",

            "curriculum",
            "curriculum_code",

            "study_program_name",
            "study_form_name",

            "semester_number",

            "code",
            "name",

            "groups_count",
            "students_count",
            "subgroups_count",

            "planned_workloads_count",
            "total_planned_hours",

            "status",
            "status_name",

            "is_active",
            "notes",

            "stream_groups",

            "created_at",
            "updated_at",

            "created_by",
            "created_by_name",

            "updated_by",
            "updated_by_name",

            "is_archived",
            "archived_at",
            "archived_by",
            "archived_by_name",
        )

        read_only_fields = (
            "id",

            "groups_count",
            "students_count",
            "subgroups_count",

            "planned_workloads_count",
            "total_planned_hours",

            "created_at",
            "updated_at",

            "created_by",
            "updated_by",

            "is_archived",
            "archived_at",
            "archived_by",
        )

    def validate_code(self, value):
        return value.strip().upper()

    def validate(self, attrs):
        instance = self.instance

        academic_year = attrs.get(
            "academic_year",
            getattr(
                instance,
                "academic_year",
                None,
            ),
        )

        academic_semester = attrs.get(
            "academic_semester",
            getattr(
                instance,
                "academic_semester",
                None,
            ),
        )

        curriculum = attrs.get(
            "curriculum",
            getattr(
                instance,
                "curriculum",
                None,
            ),
        )

        semester_number = attrs.get(
            "semester_number",
            getattr(
                instance,
                "semester_number",
                None,
            ),
        )

        if (
            academic_year
            and academic_semester
            and academic_semester.academic_year_id
            != academic_year.id
        ):
            raise serializers.ValidationError(
                {
                    "academic_semester": (
                        "Семестр не относится "
                        "к выбранному учебному году."
                    )
                }
            )

        if (
            academic_semester
            and semester_number
        ):
            expected_season = (
                "autumn"
                if semester_number % 2
                else "spring"
            )

            if (
                academic_semester.season
                != expected_season
            ):
                raise serializers.ValidationError(
                    {
                        "academic_semester": (
                            "Нечётный семестр должен "
                            "быть осенним, "
                            "чётный — весенним."
                        )
                    }
                )

        if curriculum and semester_number:
            semesters_count = (
                curriculum.semesters_count
            )

            if (
                semesters_count is not None
                and semester_number
                > semesters_count
            ):
                raise serializers.ValidationError(
                    {
                        "semester_number": (
                            "Номер семестра превышает "
                            "продолжительность обучения "
                            "по учебному плану."
                        )
                    }
                )
        return attrs

class TeachingStreamBulkSerializer(
    serializers.Serializer
):
    academic_year = (
        serializers.PrimaryKeyRelatedField(
            queryset=(
                AcademicYear.objects.filter(
                    is_archived=False,
                )
            )
        )
    )

    curriculum = (
        serializers.PrimaryKeyRelatedField(
            queryset=(
                Curriculum.objects.filter(
                    is_archived=False,
                )
            )
        )
    )

    semester_numbers = (
        serializers.ListField(
            child=serializers.IntegerField(
                min_value=1,
            ),
            allow_empty=False,
        )
    )

    code = serializers.CharField(
        max_length=100,
    )

    name = serializers.CharField(
        max_length=255,
    )

    notes = serializers.CharField(
        allow_blank=True,
        required=False,
        default="",
    )

class PlannedWorkloadSerializer(LocalizedNameMixin, AuditFieldsSerializer):
    teaching_stream_code = serializers.CharField(
        source="teaching_stream.code",
        read_only=True,
    )

    teaching_stream_name = serializers.CharField(
        source="teaching_stream.name",
        read_only=True,
    )

    academic_year_name = serializers.CharField(
        source="academic_year.name",
        read_only=True,
    )

    academic_semester_name = serializers.CharField(
        source="academic_semester.get_season_display",
        read_only=True,
    )

    curriculum = serializers.IntegerField(
        source="teaching_stream.curriculum_id",
        read_only=True,
    )

    curriculum_code = serializers.CharField(
        source="teaching_stream.curriculum.code",
        read_only=True,
    )

    curriculum_discipline = serializers.IntegerField(
        source="curriculum_workload.curriculum_discipline_id",
        read_only=True,
    )

    discipline_code = serializers.CharField(
        source=(
            "curriculum_workload."
            "curriculum_discipline."
            "discipline.code"
        ),
        read_only=True,
    )

    department_name = serializers.SerializerMethodField()
    discipline_name = serializers.SerializerMethodField()
    workload_type_name = serializers.SerializerMethodField()

    distributed_hours = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    remaining_hours = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    distribution_percent = serializers.DecimalField(
        max_digits=7,
        decimal_places=2,
        read_only=True,
    )

    is_fully_distributed = serializers.BooleanField(
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    student_group = serializers.IntegerField(
        source=(
            "group_semester."
            "group_curriculum."
            "student_group_id"
        ),
        read_only=True,
        allow_null=True,
    )

    student_group_code = serializers.CharField(
        source=(
            "group_semester."
            "group_curriculum."
            "student_group.code"
        ),
        read_only=True,
        allow_null=True,
    )

    semester_number = serializers.IntegerField(
        source=(
            "teaching_stream."
            "semester_number"
        ),
        read_only=True,
    )

    season = serializers.CharField(
        source=(
            "teaching_stream."
            "season"
        ),
        read_only=True,
    )

    @extend_schema_field(serializers.CharField())
    def get_department_name(
            self,
            obj,
    ) -> str:
        return self.get_localized_name(
            obj.teaching_department
        )

    @extend_schema_field(serializers.CharField())
    def get_discipline_name(
            self,
            obj,
    ) -> str:
        return self.get_localized_name(
            obj.curriculum_workload
            .curriculum_discipline
            .discipline
        )

    @extend_schema_field(serializers.CharField())
    def get_workload_type_name(
            self,
            obj,
    ) -> str:
        return self.get_localized_name(
            obj.curriculum_workload
            .workload_type
        )

    class Meta:
        model = PlannedWorkload

        fields = (
            "id",

            "teaching_stream",
            "teaching_stream_code",
            "teaching_stream_name",

            "curriculum",
            "curriculum_code",

            "curriculum_discipline",
            "discipline_code",
            "discipline_name",

            "academic_year",
            "academic_year_name",

            "academic_semester",
            "academic_semester_name",

            "teaching_department",
            "department_name",

            "curriculum_workload",
            "workload_type_name",

            "calculation_mode",

            "base_hours",
            "calculation_quantity",
            "total_hours",

            "distributed_hours",
            "remaining_hours",
            "distribution_percent",
            "is_fully_distributed",

            "groups_count",
            "subgroups_count",
            "students_count",

            "group_semester",
            "student_group",
            "student_group_code",

            "semester_number",
            "season",

            "status",
            "status_name",

            "calculated_at",

            "notes",

            "created_at",
            "updated_at",

            "created_by",
            "created_by_name",

            "updated_by",
            "updated_by_name",

            "is_archived",
            "archived_at",
            "archived_by",
            "archived_by_name",
        )

        read_only_fields = fields
