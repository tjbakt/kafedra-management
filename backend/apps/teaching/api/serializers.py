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

        return attrs

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
            != stream.curriculum_discipline.curriculum_id
        ):
            raise serializers.ValidationError(
                {
                    "group_semester": (
                        "Учебный план группы не совпадает с учебным планом дисциплины."
                    )
                }
            )

        if (
            group_semester.semester_number
            != stream.curriculum_discipline.semester_number
        ):
            raise serializers.ValidationError(
                {
                    "group_semester": (
                        "Номер семестра группы не совпадает с номером семестра дисциплины."
                    )
                }
            )

        return attrs

class TeachingStreamSerializer(AuditFieldsSerializer):
    academic_year_name = serializers.CharField(
        source="academic_year.name",
        read_only=True,
    )
    academic_semester_name = serializers.CharField(
        source="academic_semester.get_season_display",
        read_only=True,
    )
    discipline_name = serializers.CharField(
        source="curriculum_discipline.discipline.name_ru",
        read_only=True,
    )
    semester_number = serializers.IntegerField(
        source="curriculum_discipline.semester_number",
        read_only=True,
    )
    workload_type = serializers.IntegerField(
        source="curriculum_workload.workload_type_id",
        read_only=True,
    )
    workload_type_name = serializers.CharField(
        source="curriculum_workload.workload_type.name_ru",
        read_only=True,
    )
    calculation_mode = serializers.CharField(
        source="curriculum_workload.calculation_mode",
        read_only=True,
    )
    teaching_department_name = serializers.CharField(
        source="teaching_department.name_ru",
        read_only=True,
    )
    groups_count = serializers.IntegerField(read_only=True)
    students_count = serializers.IntegerField(read_only=True)
    subgroups_count = serializers.IntegerField(read_only=True)
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    stream_groups = TeachingStreamGroupSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = TeachingStream
        fields = (
            "id",
            "academic_year",
            "academic_year_name",
            "academic_semester",
            "academic_semester_name",
            "curriculum_discipline",
            "discipline_name",
            "semester_number",
            "curriculum_workload",
            "workload_type",
            "workload_type_name",
            "calculation_mode",
            "teaching_department",
            "teaching_department_name",
            "code",
            "name",
            "groups_count",
            "students_count",
            "subgroups_count",
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
            "workload_type",
            "calculation_mode",
            "groups_count",
            "students_count",
            "subgroups_count",
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

        discipline = attrs.get(
            "curriculum_discipline",
            getattr(instance, "curriculum_discipline", None),
        )
        workload = attrs.get(
            "curriculum_workload",
            getattr(instance, "curriculum_workload", None),
        )
        department = attrs.get(
            "teaching_department",
            getattr(instance, "teaching_department", None),
        )
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

        if (
            discipline
            and workload
            and workload.curriculum_discipline_id
            != discipline.id
        ):
            raise serializers.ValidationError(
                {
                    "curriculum_workload": (
                        "Выбранный вид нагрузки не относится "
                        "к дисциплине."
                    )
                }
            )

        if (
            discipline
            and department
            and discipline.teaching_department_id
            != department.id
        ):
            raise serializers.ValidationError(
                {
                    "teaching_department": (
                        "Кафедра потока должна совпадать "
                        "с обеспечивающей кафедрой дисциплины."
                    )
                }
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
                        "Семестр должен относиться "
                        "к выбранному учебному году."
                    )
                }
            )

        if discipline and academic_semester:
            expected_season = (
                "autumn"
                if discipline.semester_number % 2
                else "spring"
            )

            if (
                academic_semester.season
                != expected_season
            ):
                raise serializers.ValidationError(
                    {
                        "academic_semester": (
                            "Сезон потока не соответствует "
                            "номеру семестра дисциплины."
                        )
                    }
                )
        return attrs

class PlannedWorkloadSerializer(AuditFieldsSerializer):
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
    department_name = serializers.CharField(
        source="teaching_department.name_ru",
        read_only=True,
    )
    discipline_name = serializers.CharField(
        source=(
            "teaching_stream.curriculum_discipline."
            "discipline.name_ru"
        ),
        read_only=True,
    )
    workload_type_name = serializers.CharField(
        source="curriculum_workload.workload_type.name_ru",
        read_only=True,
    )
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = PlannedWorkload
        fields = (
            "id",
            "teaching_stream",
            "teaching_stream_code",
            "teaching_stream_name",
            "academic_year",
            "academic_year_name",
            "academic_semester",
            "academic_semester_name",
            "teaching_department",
            "department_name",
            "discipline_name",
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
        read_only_fields = (
            "id",
            "teaching_stream",
            "academic_year",
            "academic_semester",
            "teaching_department",
            "curriculum_workload",
            "calculation_mode",
            "base_hours",
            "calculation_quantity",
            "total_hours",
            "groups_count",
            "subgroups_count",
            "students_count",
            "calculated_at",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

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
        max_digits=8,
        decimal_places=2,
        read_only=True,
    )
    is_fully_distributed = serializers.BooleanField(
        read_only=True,
    )