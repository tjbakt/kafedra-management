from decimal import Decimal

from django.db import transaction
from django.utils.translation import get_language
from rest_framework import serializers

from apps.common.api.serializers import AuditFieldsSerializer
from apps.curriculum.models import (
    Curriculum,
    CurriculumDiscipline,
    CurriculumWorkload,
    Discipline,
    WorkloadType,
)
from drf_spectacular.utils import (
    extend_schema_field,
)


class LocalizedNameMixin:
    @extend_schema_field(
        serializers.CharField()
    )
    def get_display_name(self, obj) -> str:
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

class DisciplineSerializer(
    LocalizedNameMixin,
    AuditFieldsSerializer,
):
    display_name = serializers.SerializerMethodField()
    default_department_name = serializers.CharField(
        source="default_department.name_ru",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Discipline
        fields = (
            "id",
            "code",
            "name_ru",
            "name_uz",
            "display_name",
            "default_department",
            "default_department_name",
            "is_active",
            "sort_order",
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
            "display_name",
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


class WorkloadTypeSerializer(
    LocalizedNameMixin,
    AuditFieldsSerializer,
):
    display_name = serializers.SerializerMethodField()
    calculation_mode_name = serializers.CharField(
        source="get_calculation_mode_display",
        read_only=True,
    )

    class Meta:
        model = WorkloadType
        fields = (
            "id",
            "code",
            "name_ru",
            "name_uz",
            "display_name",
            "calculation_mode",
            "calculation_mode_name",
            "is_classroom",
            "is_teaching_load",
            "is_active",
            "sort_order",
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
            "display_name",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

class CurriculumWorkloadSerializer(AuditFieldsSerializer):
    workload_type_name = serializers.CharField(
        source="workload_type.name_ru",
        read_only=True,
    )
    calculation_mode_name = serializers.CharField(
        source="get_calculation_mode_display",
        read_only=True,
    )

    class Meta:
        model = CurriculumWorkload
        fields = (
            "id",
            "curriculum_discipline",
            "workload_type",
            "workload_type_name",
            "calculation_mode",
            "calculation_mode_name",
            "base_hours",
            "students_per_unit",
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
        workload_type = attrs.get(
            "workload_type",
            getattr(self.instance, "workload_type", None),
        )
        calculation_mode = attrs.get("calculation_mode")

        if workload_type and calculation_mode is None:
            attrs["calculation_mode"] = (
                workload_type.calculation_mode
            )

        return attrs

class CurriculumDisciplineSerializer(
    AuditFieldsSerializer,
):
    discipline_code = serializers.CharField(
        source="discipline.code",
        read_only=True,
    )
    discipline_name = serializers.CharField(
        source="discipline.name_ru",
        read_only=True,
    )
    teaching_department_name = serializers.CharField(
        source="teaching_department.name_ru",
        read_only=True,
    )
    control_form_name = serializers.CharField(
        source="get_control_form_display",
        read_only=True,
    )
    component_type_name = serializers.CharField(
        source="get_component_type_display",
        read_only=True,
    )
    season = serializers.CharField(read_only=True)
    season_name = serializers.CharField(read_only=True)
    planned_contact_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    workload_items = CurriculumWorkloadSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = CurriculumDiscipline
        fields = (
            "id",
            "curriculum",
            "discipline",
            "discipline_code",
            "discipline_name",
            "semester_number",
            "season",
            "season_name",
            "teaching_department",
            "teaching_department_name",
            "component_type",
            "component_type_name",
            "control_form",
            "control_form_name",
            "credits",
            "total_academic_hours",
            "independent_hours",
            "planned_contact_hours",
            "weeks_count",
            "is_active",
            "notes",
            "workload_items",
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
            "season",
            "season_name",
            "planned_contact_hours",
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

        curriculum = attrs.get(
            "curriculum",
            getattr(instance, "curriculum", None),
        )
        semester_number = attrs.get(
            "semester_number",
            getattr(instance, "semester_number", None),
        )
        teaching_department = attrs.get(
            "teaching_department",
            getattr(instance, "teaching_department", None),
        )
        total_hours = attrs.get(
            "total_academic_hours",
            getattr(
                instance,
                "total_academic_hours",
                Decimal("0.00"),
            ),
        )
        independent_hours = attrs.get(
            "independent_hours",
            getattr(
                instance,
                "independent_hours",
                Decimal("0.00"),
            ),
        )

        if curriculum and semester_number:
            semesters_count = curriculum.semesters_count

            if (
                semesters_count
                and semester_number > semesters_count
            ):
                raise serializers.ValidationError(
                    {
                        "semester_number": (
                            "Номер семестра превышает длительность "
                            "обучения по учебному плану."
                        )
                    }
                )

        if curriculum and teaching_department:
            if (
                curriculum.study_program.university_id
                != teaching_department.faculty.university_id
            ):
                raise serializers.ValidationError(
                    {
                        "teaching_department": (
                            "Кафедра должна относиться к университету "
                            "учебного плана."
                        )
                    }
                )

        if independent_hours > total_hours:
            raise serializers.ValidationError(
                {
                    "independent_hours": (
                        "Самостоятельные часы не могут превышать "
                        "общий объём дисциплины."
                    )
                }
            )

        return attrs

class CurriculumSerializer(AuditFieldsSerializer):
    study_program_code = serializers.CharField(
        source="study_program.code",
        read_only=True,
    )
    study_program_name = serializers.CharField(
        source="study_program.name_ru",
        read_only=True,
    )
    education_level = serializers.IntegerField(
        source="study_program.education_level_id",
        read_only=True,
    )
    education_level_name = serializers.CharField(
        source="study_program.education_level.name_ru",
        read_only=True,
    )
    study_form_name = serializers.CharField(
        source="study_form.name_ru",
        read_only=True,
    )
    effective_academic_year_name = serializers.CharField(
        source="effective_academic_year.name",
        read_only=True,
    )
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    semesters_count = serializers.IntegerField(
        read_only=True,
        allow_null=True,
    )
    disciplines_count = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Curriculum
        fields = (
            "id",
            "code",
            "version",
            "study_program",
            "study_program_code",
            "study_program_name",
            "education_level",
            "education_level_name",
            "study_form",
            "study_form_name",
            "effective_academic_year",
            "effective_academic_year_name",
            "semesters_count",
            "status",
            "status_name",
            "approved_at",
            "approval_document",
            "is_active",
            "notes",
            "disciplines_count",
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
            "education_level",
            "semesters_count",
            "disciplines_count",
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

        study_program = attrs.get(
            "study_program",
            getattr(instance, "study_program", None),
        )
        study_form = attrs.get(
            "study_form",
            getattr(instance, "study_form", None),
        )
        status_value = attrs.get(
            "status",
            getattr(instance, "status", Curriculum.Status.DRAFT),
        )
        approved_at = attrs.get(
            "approved_at",
            getattr(instance, "approved_at", None),
        )

        if (
            status_value == Curriculum.Status.APPROVED
            and not approved_at
        ):
            raise serializers.ValidationError(
                {
                    "approved_at": (
                        "Для утверждённого плана необходимо "
                        "указать дату утверждения."
                    )
                }
            )

        if study_program and study_form:
            from apps.academics.models import EducationDuration

            duration_exists = EducationDuration.objects.filter(
                education_level=study_program.education_level,
                study_form=study_form,
                is_active=True,
            ).exists()

            if not duration_exists:
                raise serializers.ValidationError(
                    {
                        "study_form": (
                            "Для выбранной степени и формы обучения "
                            "не настроена продолжительность."
                        )
                    }
                )

        return attrs