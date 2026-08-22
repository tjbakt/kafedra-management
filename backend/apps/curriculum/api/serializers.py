from decimal import Decimal

from django.db import transaction
from django.utils.translation import get_language
from rest_framework import serializers

from apps.common.api.serializers import AuditFieldsSerializer
from apps.curriculum.models import (
    AcademicYearCreditNorm,
    AcademicYearWorkloadNorm,
    Curriculum,
    CurriculumDiscipline,
    CurriculumWorkload,
    CurriculumWorkloadRule,
    Discipline,
    WorkloadType,
)
from drf_spectacular.utils import (
    extend_schema_field,
)
from apps.curriculum.services.norm_resolver import (
    resolve_curriculum_academic_year,
    resolve_curriculum_credit_norm,
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
    default_department_name = serializers.SerializerMethodField()

    workload_types = (
        serializers.PrimaryKeyRelatedField(
            queryset=WorkloadType.objects.filter(
                is_archived=False,
            ),
            many=True,
            required=False,
        )
    )

    workload_type_details = (
        serializers.SerializerMethodField()
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
            "workload_types",
            "workload_type_details",
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
            "workload_type_details",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

    @extend_schema_field(
        serializers.ListField(
            child=serializers.DictField()
        )
    )
    def get_workload_type_details(
        self,
        obj,
    ):
        return [
            {
                "id": item.id,
                "code": item.code,
                "display_name":
                    self.get_display_name(
                        item
                    ),
                "calculation_mode":
                    item.calculation_mode,
                "is_classroom":
                    item.is_classroom,
                "is_teaching_load":
                    item.is_teaching_load,
                "uses_annual_norm":
                    item.uses_annual_norm,
                "paired_code":
                    item.paired_code,
            }
            for item
            in obj.workload_types
            .filter(
                is_archived=False
            )
            .order_by(
                "sort_order",
                "name_ru",
            )
        ]

    def validate_workload_types(
        self,
        workload_types,
    ):
        codes = {
            item.code
            for item in workload_types
        }

        #
        # КР и КП одновременно запрещены.
        #
        course_work_selected = bool(
            {
                WorkloadType
                .Code
                .COURSE_WORK_SUPERVISION,

                WorkloadType
                .Code
                .COURSE_WORK_DEFENSE,
            }
            & codes
        )

        course_project_selected = bool(
            {
                WorkloadType
                .Code
                .COURSE_PROJECT_SUPERVISION,

                WorkloadType
                .Code
                .COURSE_PROJECT_DEFENSE,
            }
            & codes
        )

        if (
            course_work_selected
            and course_project_selected
        ):
            raise serializers.ValidationError(
                "Для одной дисциплины нельзя "
                "одновременно выбирать курсовую "
                "работу и курсовой проект."
            )

        #
        # ВКР и магистерская диссертация
        # одновременно запрещены.
        #
        graduation_selected = bool(
            {
                WorkloadType
                .Code
                .GRADUATION_WORK_SUPERVISION,

                WorkloadType
                .Code
                .GRADUATION_WORK_DEFENSE,
            }
            & codes
        )

        master_selected = bool(
            {
                WorkloadType
                .Code
                .MASTER_DISSERTATION_SUPERVISION,

                WorkloadType
                .Code
                .MASTER_DISSERTATION_DEFENSE,
            }
            & codes
        )

        if (
            graduation_selected
            and master_selected
        ):
            raise serializers.ValidationError(
                "Нельзя одновременно выбирать "
                "выпускную квалификационную работу "
                "и магистерскую диссертацию."
            )

        #
        # Парные виды должны присутствовать вместе.
        #
        for item in workload_types:
            paired_code = (
                item.paired_code
            )

            if (
                paired_code
                and paired_code
                not in codes
            ):
                raise serializers.ValidationError(
                    (
                        f"Для вида работы "
                        f"«{item.name_ru}» необходимо "
                        f"также выбрать связанный "
                        f"вид работы."
                    )
                )

        return workload_types

    @extend_schema_field(
        serializers.CharField(
            allow_null=True,
        )
    )
    def get_default_department_name(self, obj):
        if not obj.default_department:
            return None

        return self.get_display_name(
            obj.default_department
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
    report_category_name = serializers.CharField(
        source="get_report_category_display",
        read_only=True,
    )
    uses_annual_norm = (
        serializers.BooleanField(
            read_only=True,
        )
    )

    uses_curriculum_rule = (
        serializers.BooleanField(
            read_only=True,
        )
    )

    paired_code = (
        serializers.CharField(
            read_only=True,
            allow_null=True,
        )
    )

    uses_weekly_norm = serializers.BooleanField(
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
            "report_category",
            "report_category_name",
            "is_classroom",
            "is_teaching_load",
            "uses_annual_norm",
            "uses_curriculum_rule",
            "paired_code",
            "uses_weekly_norm",
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

class CurriculumWorkloadSerializer(LocalizedNameMixin, AuditFieldsSerializer):
    calculation_mode = serializers.ChoiceField(
        choices=(
            WorkloadType
            .CalculationMode
            .choices
        ),
        required=False,
    )
    workload_type_name = serializers.SerializerMethodField()
    calculation_mode_name = serializers.CharField(
        source="get_calculation_mode_display",
        read_only=True,
    )
    uses_curriculum_rule = (
        serializers.BooleanField(
            source=(
                "workload_type."
                "uses_curriculum_rule"
            ),
            read_only=True,
        )
    )

    class Meta:
        model = CurriculumWorkload
        fields = (
            "id",
            "curriculum_discipline",
            "workload_type",
            "workload_type_name",
            "uses_curriculum_rule",
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
            "workload_type_name",
            "calculation_mode_name",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

    @extend_schema_field(serializers.CharField())
    def get_workload_type_name(self, obj) -> str:
        if not obj.workload_type:
            return ""

        return self.get_display_name(obj.workload_type)

    def validate(self, attrs):
        instance = self.instance

        workload_type = attrs.get(
            "workload_type",
            getattr(
                instance,
                "workload_type",
                None,
            ),
        )

        curriculum_discipline = (
            attrs.get(
                "curriculum_discipline",
                getattr(
                    instance,
                    "curriculum_discipline",
                    None,
                ),
            )
        )

        if (
                workload_type
                and workload_type
                .uses_curriculum_rule
        ):
            if not curriculum_discipline:
                return attrs

            rule = (
                CurriculumWorkloadRule
                .objects
                .filter(
                    curriculum=(
                        curriculum_discipline
                        .curriculum
                    ),
                    workload_type=(
                        workload_type
                    ),
                    is_active=True,
                    is_archived=False,
                )
                .first()
            )

            if not rule:
                raise serializers.ValidationError(
                    {
                        "workload_type": (
                            "Для этого вида работы "
                            "не задана единая норма "
                            "учебного плана."
                        )
                    }
                )

            attrs["calculation_mode"] = (
                rule.calculation_mode
            )

            attrs["base_hours"] = (
                rule.base_hours
            )

            attrs["students_per_unit"] = (
                rule.students_per_unit
            )

            return attrs

        calculation_mode = attrs.get(
            "calculation_mode",
            getattr(
                instance,
                "calculation_mode",
                None,
            ),
        )

        if (
                workload_type
                and not calculation_mode
        ):
            attrs["calculation_mode"] = (
                workload_type.calculation_mode
            )

            calculation_mode = (
                workload_type.calculation_mode
            )

        base_hours = attrs.get(
            "base_hours",
            getattr(
                instance,
                "base_hours",
                Decimal("0.00"),
            ),
        )

        if (
                calculation_mode
                == WorkloadType
                .CalculationMode
                .PER_STUDENT
                and base_hours <= 0
        ):
            raise serializers.ValidationError(
                {
                    "base_hours": (
                        "Количество часов "
                        "должно быть больше нуля."
                    )
                }
            )

        return attrs

class CurriculumDisciplineSerializer(LocalizedNameMixin, AuditFieldsSerializer,):
    discipline_code = serializers.CharField(
        source="discipline.code",
        read_only=True,
    )
    discipline_name = serializers.SerializerMethodField()
    teaching_department_name = serializers.SerializerMethodField()
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

    @extend_schema_field(serializers.CharField())
    def get_discipline_name(self, obj) -> str:
        return self.get_display_name(
            obj.discipline
        )

    @extend_schema_field(serializers.CharField())
    def get_teaching_department_name(
            self,
            obj,
    ) -> str:
        return self.get_display_name(
            obj.teaching_department
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
            "teaching_department",
            "teaching_department_name",
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
            getattr(
                instance,
                "curriculum",
                None,
            ),
        )

        discipline = attrs.get(
            "discipline",
            getattr(
                instance,
                "discipline",
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

        if discipline:
            if not discipline.default_department:
                raise serializers.ValidationError(
                    {
                        "discipline": (
                            "Для дисциплины не задана "
                            "кафедра по умолчанию."
                        )
                    }
                )

            if curriculum:
                if (
                        discipline
                                .default_department
                                .faculty
                                .university_id
                        != curriculum
                        .study_program
                        .university_id
                ):
                    raise serializers.ValidationError(
                        {
                            "discipline": (
                                "Кафедра дисциплины "
                                "не относится к университету "
                                "учебного плана."
                            )
                        }
                    )

        if (
                curriculum
                and semester_number
        ):
            semesters_count = (
                curriculum.semesters_count
            )

            if (
                    semesters_count
                    and semester_number >
                    semesters_count
            ):
                raise serializers.ValidationError(
                    {
                        "semester_number": (
                            "Номер семестра превышает "
                            "длительность обучения."
                        )
                    }
                )

        return attrs

    def create(self, validated_data):
        discipline = (
            validated_data["discipline"]
        )

        validated_data[
            "teaching_department"
        ] = discipline.default_department

        validated_data.setdefault(
            "control_form",
            CurriculumDiscipline
            .ControlForm
            .NONE,
        )

        return super().create(
            validated_data
        )

    def update(
            self,
            instance,
            validated_data,
    ):
        discipline = validated_data.get(
            "discipline",
            instance.discipline,
        )

        validated_data[
            "teaching_department"
        ] = discipline.default_department

        return super().update(
            instance,
            validated_data,
        )

class CurriculumSerializer(LocalizedNameMixin, AuditFieldsSerializer):
    study_program_code = serializers.CharField(
        source="study_program.code",
        read_only=True,
    )
    education_level = serializers.IntegerField(
        source="study_program.education_level_id",
        read_only=True,
    )
    study_program_name = serializers.SerializerMethodField()
    education_level_name = serializers.SerializerMethodField()
    study_form_name = serializers.SerializerMethodField()

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

    @extend_schema_field(serializers.CharField())
    def get_study_program_name(self, obj) -> str:
        return self.get_display_name(
            obj.study_program
        )

    @extend_schema_field(serializers.CharField())
    def get_education_level_name(self, obj) -> str:
        return self.get_display_name(
            obj.study_program.education_level
        )

    @extend_schema_field(serializers.CharField())
    def get_study_form_name(self, obj) -> str:
        return self.get_display_name(
            obj.study_form
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

class CurriculumWorkloadRuleSerializer(
    LocalizedNameMixin,
    AuditFieldsSerializer,
):
    workload_type_name = (
        serializers.SerializerMethodField()
    )

    calculation_mode_name = (
        serializers.CharField(
            source=(
                "get_calculation_mode_display"
            ),
            read_only=True,
        )
    )

    @extend_schema_field(
        serializers.CharField()
    )
    def get_workload_type_name(
        self,
        obj,
    ) -> str:
        return self.get_display_name(
            obj.workload_type
        )

    class Meta:
        model = CurriculumWorkloadRule

        fields = (
            "id",

            "curriculum",

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

            "workload_type_name",
            "calculation_mode_name",

            "created_at",
            "updated_at",

            "created_by",
            "updated_by",

            "is_archived",
            "archived_at",
            "archived_by",
        )

    def validate(
        self,
        attrs,
    ):
        workload_type = attrs.get(
            "workload_type",
            getattr(
                self.instance,
                "workload_type",
                None,
            ),
        )

        if (
            workload_type
            and not
            workload_type
            .uses_curriculum_rule
        ):
            raise serializers.ValidationError(
                {
                    "workload_type": (
                        "Для этого вида работы "
                        "не предусмотрена единая "
                        "норма учебного плана."
                    )
                }
            )

        return attrs

class CurriculumBundleWorkloadInputSerializer(
    serializers.Serializer
):
    workload_type = (
        serializers.PrimaryKeyRelatedField(
            queryset=(
                WorkloadType.objects.filter(
                    is_active=True,
                    is_archived=False,
                )
            )
        )
    )

    calculation_mode = (
        serializers.ChoiceField(
            choices=(
                WorkloadType
                .CalculationMode
                .choices
            ),
            required=False,
        )
    )

    base_hours = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=Decimal("0.00"),
        required=False,
        default=Decimal("0.00"),
    )

    students_per_unit = (
        serializers.IntegerField(
            min_value=1,
            required=False,
            allow_null=True,
        )
    )

    is_active = serializers.BooleanField(
        default=True,
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


class CurriculumBundleSemesterSerializer(
    serializers.Serializer
):
    semester_number = (
        serializers.IntegerField(
            min_value=1,
        )
    )

    credits = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=Decimal("0.00"),
        default=Decimal("0.00"),
    )

    weeks_count = (
        serializers.IntegerField(
            min_value=1,
            default=15,
        )
    )

    is_active = serializers.BooleanField(
        default=True,
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    workloads = (
        CurriculumBundleWorkloadInputSerializer(
            many=True,
            default=list,
        )
    )


class CurriculumDisciplineBundleSerializer(
    serializers.Serializer
):
    curriculum = (
        serializers.PrimaryKeyRelatedField(
            queryset=Curriculum.objects.filter(
                is_archived=False,
            )
        )
    )

    discipline = (
        serializers.PrimaryKeyRelatedField(
            queryset=Discipline.objects.filter(
                is_archived=False,
            )
        )
    )

    component_type = (
        serializers.ChoiceField(
            choices=(
                CurriculumDiscipline
                .ComponentType
                .choices
            ),
            default=(
                CurriculumDiscipline
                .ComponentType
                .REQUIRED
            ),
        )
    )

    semesters = (
        CurriculumBundleSemesterSerializer(
            many=True,
        )
    )

    replace_semesters = (
        serializers.BooleanField(
            default=True,
        )
    )

    def validate(self, attrs):
        curriculum = attrs["curriculum"]
        discipline = attrs["discipline"]

        allowed_workload_ids = set(
            discipline
            .workload_types
            .filter(
                is_active=True,
                is_archived=False,
            )
            .values_list(
                "id",
                flat=True,
            )
        )

        # academic_year = (
        #     curriculum
        #     .effective_academic_year
        # )

        curriculum_academic_year = (
            resolve_curriculum_academic_year(
                curriculum
            )
        )

        credit_norm = (
            resolve_curriculum_credit_norm(
                curriculum
            )
        )

        if not credit_norm:
            raise serializers.ValidationError(
                {
                    "curriculum": (
                        "Для учебного года "
                        f"{curriculum_academic_year} "
                        "не задано количество "
                        "часов на один "
                        "академический кредит."
                    )
                }
            )

        if not credit_norm:
            raise serializers.ValidationError(
                {
                    "curriculum": (
                        "Не задана ни одна "
                        "действующая норма "
                        "академического кредита "
                        "для года начала действия "
                        "учебного плана."
                    )
                }
            )

        department = (
            discipline.default_department
        )

        if not department:
            raise serializers.ValidationError(
                {
                    "discipline": (
                        "У выбранной дисциплины "
                        "не задана кафедра."
                    )
                }
            )

        if (
            department.faculty.university_id
            != curriculum
            .study_program
            .university_id
        ):
            raise serializers.ValidationError(
                {
                    "discipline": (
                        "Кафедра дисциплины "
                        "не относится к университету "
                        "учебного плана."
                    )
                }
            )

        semesters = attrs["semesters"]

        if not semesters:
            raise serializers.ValidationError(
                {
                    "semesters": (
                        "Выберите хотя бы "
                        "один семестр."
                    )
                }
            )

        semester_numbers = [
            item["semester_number"]
            for item in semesters
        ]

        if (
            len(semester_numbers)
            != len(set(semester_numbers))
        ):
            raise serializers.ValidationError(
                {
                    "semesters": (
                        "Один семестр указан "
                        "несколько раз."
                    )
                }
            )

        semesters_count = (
            curriculum.semesters_count
        )

        for semester in semesters:
            semester_number = (
                semester[
                    "semester_number"
                ]
            )

            if (
                semesters_count
                and semester_number >
                semesters_count
            ):
                raise serializers.ValidationError(
                    {
                        "semesters": (
                            f"Семестр "
                            f"{semester_number} "
                            "выходит за пределы "
                            "учебного плана."
                        )
                    }
                )

            workload_ids = [
                item["workload_type"].id
                for item
                in semester["workloads"]
            ]

            if (
                len(workload_ids)
                != len(
                    set(workload_ids)
                )
            ):
                raise serializers.ValidationError(
                    {
                        "semesters": (
                            f"В семестре "
                            f"{semester_number} "
                            "один вид нагрузки "
                            "добавлен несколько раз."
                        )
                    }
                )

            for workload in ( semester["workloads"] ):
                workload_type = (
                    workload[
                        "workload_type"
                    ]
                )

                if (
                        workload_type.id
                        not in
                        allowed_workload_ids
                ):
                    raise serializers.ValidationError(
                        {
                            "semesters": (
                                f"Вид работы "
                                f"«{workload_type.name_ru}» "
                                "не разрешён для "
                                "выбранной дисциплины."
                            )
                        }
                    )

                    if not norm_exists:
                        raise serializers.ValidationError(
                            {
                                "semesters": (
                                    f"Для "
                                    f"«{workload_type.name_ru}» "
                                    "не установлена норма "
                                    "на учебный год."
                                )
                            }
                        )

        return attrs

    @staticmethod
    def resolve_workload_values(
        *,
        curriculum,
        workload_data,
    ):
        workload_type = (
            workload_data[
                "workload_type"
            ]
        )

        if (
            workload_type.uses_annual_norm
        ):
            calculation_mode = (
                WorkloadType
                .CalculationMode
                .PER_GROUP
                if workload_type
                .uses_weekly_norm
                else workload_type
                .calculation_mode
            )

            return {
                "calculation_mode": calculation_mode,

                "base_hours": Decimal("0.00"),

                "students_per_unit": None,
            }

        return {
            "calculation_mode":
                workload_data.get(
                    "calculation_mode"
                )
                or workload_type
                .calculation_mode,

            "base_hours":
                workload_data.get(
                    "base_hours",
                    Decimal("0.00"),
                ),

            "students_per_unit":
                workload_data.get(
                    "students_per_unit"
                ),
        }

    @transaction.atomic
    def create(self, validated_data):
        curriculum = (
            validated_data[
                "curriculum"
            ]
        )

        discipline = (
            validated_data[
                "discipline"
            ]
        )

        component_type = (
            validated_data[
                "component_type"
            ]
        )

        semesters = (
            validated_data[
                "semesters"
            ]
        )

        replace_semesters = (
            validated_data[
                "replace_semesters"
            ]
        )

        user = None

        request = self.context.get(
            "request"
        )

        if (
            request
            and request.user
            and request.user
            .is_authenticated
        ):
            user = request.user

        submitted_semesters = set()

        result = []

        classroom_codes = {
            WorkloadType.Code.LECTURE,
            WorkloadType.Code.PRACTICE,
            WorkloadType.Code.LABORATORY,
            WorkloadType.Code.SEMINAR,
        }

        for semester in semesters:
            semester_number = (
                semester[
                    "semester_number"
                ]
            )

            submitted_semesters.add(
                semester_number
            )

            resolved_workloads = []

            classroom_hours = (
                Decimal("0.00")
            )

            independent_hours = (
                Decimal("0.00")
            )

            practice_hours = Decimal("0.00")

            for workload in (
                semester["workloads"]
            ):
                workload_type = (
                    workload[
                        "workload_type"
                    ]
                )

                if workload_type.uses_weekly_norm:
                    norm = (
                        AcademicYearWorkloadNorm
                        .objects
                        .filter(
                            academic_year=(
                                resolve_curriculum_academic_year(
                                    curriculum
                                )
                            ),
                            workload_type=(
                                workload_type
                            ),
                            is_active=True,
                            is_archived=False,
                        )
                        .first()
                    )

                    if not norm:
                        raise serializers.ValidationError(
                            {
                                "semesters": (
                                    "Для вида работы "
                                    f"«{workload_type.name_ru}» "
                                    "не задана годовая норма."
                                )
                            }
                        )

                    if workload.get(
                            "is_active",
                            True,
                    ):
                        practice_hours += (
                                norm.coefficient
                                *
                                Decimal(
                                    semester[
                                        "weeks_count"
                                    ]
                                )
                        )

                values = (
                    self
                    .resolve_workload_values(
                        curriculum=curriculum,
                        workload_data=workload,
                    )
                )

                resolved_workloads.append(
                    (
                        workload,
                        values,
                    )
                )

                if (
                    workload_type.code
                    in classroom_codes
                ):
                    classroom_hours += (
                        values[
                            "base_hours"
                        ]
                    )

                if (
                    workload_type.code
                    == WorkloadType
                    .Code
                    .INDEPENDENT_WORK
                ):
                    independent_hours += (
                        values[
                            "base_hours"
                        ]
                    )

            total_hours = (
                classroom_hours
                + independent_hours
                + practice_hours
            )

            credit_norm = (
                resolve_curriculum_credit_norm(
                    curriculum
                )
            )

            if not credit_norm:
                academic_year = (
                    resolve_curriculum_academic_year(
                        curriculum
                    )
                )

                raise serializers.ValidationError(
                    {
                        "curriculum": (
                            "Для учебного года "
                            f"{academic_year} "
                            "не задано количество "
                            "часов на один "
                            "академический кредит."
                        )
                    }
                )

            credits = (
                total_hours
                /
                credit_norm
                .hours_per_credit
                if total_hours > 0
                else Decimal("0.00")
            ).quantize(
                Decimal("0.01")
            )

            discipline_entry = (
                CurriculumDiscipline
                .all_objects
                .filter(
                    curriculum=curriculum,
                    discipline=discipline,
                    semester_number=(
                        semester_number
                    ),
                )
                .first()
            )

            defaults = {
                "teaching_department":
                    discipline
                    .default_department,

                "component_type":
                    component_type,

                "control_form":
                    (
                        discipline_entry
                        .control_form
                        if discipline_entry
                        else
                        CurriculumDiscipline
                        .ControlForm
                        .NONE
                    ),

                "credits": credits,

                "total_academic_hours":
                    total_hours,

                "independent_hours":
                    independent_hours,

                "weeks_count":
                    semester[
                        "weeks_count"
                    ],

                "is_active":
                    semester[
                        "is_active"
                    ],

                "notes":
                    semester[
                        "notes"
                    ],

                "updated_by":
                    user,

                "is_archived":
                    False,

                "archived_at":
                    None,

                "archived_by":
                    None,
            }

            if discipline_entry:
                for field, value in (
                    defaults.items()
                ):
                    setattr(
                        discipline_entry,
                        field,
                        value,
                    )

                discipline_entry.save()

            else:
                discipline_entry = (
                    CurriculumDiscipline
                    .objects.create(
                        curriculum=curriculum,
                        discipline=discipline,
                        semester_number=(
                            semester_number
                        ),
                        created_by=user,
                        **defaults,
                    )
                )

            submitted_workload_ids = set()

            for (
                workload_data,
                values,
            ) in resolved_workloads:
                workload_type = (
                    workload_data[
                        "workload_type"
                    ]
                )

                submitted_workload_ids.add(
                    workload_type.id
                )

                existing = (
                    CurriculumWorkload
                    .all_objects
                    .filter(
                        curriculum_discipline=(
                            discipline_entry
                        ),
                        workload_type=(
                            workload_type
                        ),
                    )
                    .first()
                )

                workload_defaults = {
                    **values,

                    "is_active":
                        workload_data[
                            "is_active"
                        ],

                    "notes":
                        workload_data[
                            "notes"
                        ],

                    "updated_by":
                        user,

                    "is_archived":
                        False,

                    "archived_at":
                        None,

                    "archived_by":
                        None,
                }

                if existing:
                    for (
                        field,
                        value,
                    ) in (
                        workload_defaults
                        .items()
                    ):
                        setattr(
                            existing,
                            field,
                            value,
                        )

                    existing.save()

                else:
                    CurriculumWorkload.objects.create(
                        curriculum_discipline=(
                            discipline_entry
                        ),
                        workload_type=(
                            workload_type
                        ),
                        created_by=user,
                        **workload_defaults,
                    )

            #
            # Не выбранный в новой форме
            # вид нагрузки не удаляем
            # физически — делаем неактивным.
            #
            (
                discipline_entry
                .workload_items
                .filter(
                    is_archived=False,
                )
                .exclude(
                    workload_type_id__in=(
                        submitted_workload_ids
                    )
                )
                .update(
                    is_active=False,
                )
            )

            result.append(
                discipline_entry
            )

        if replace_semesters:
            (
                CurriculumDiscipline.objects
                .filter(
                    curriculum=curriculum,
                    discipline=discipline,
                )
                .exclude(
                    semester_number__in=(
                        submitted_semesters
                    )
                )
                .update(
                    is_active=False,
                )
            )

        return result

class AcademicYearWorkloadNormSerializer(
    LocalizedNameMixin,
    AuditFieldsSerializer,
):
    workload_type_name = (
        serializers.SerializerMethodField()
    )

    academic_year_name = (
        serializers.CharField(
            source="academic_year.name",
            read_only=True,
        )
    )

    @extend_schema_field(
        serializers.CharField()
    )
    def get_workload_type_name(
        self,
        obj,
    ):
        return self.get_display_name(
            obj.workload_type
        )

    class Meta:
        model = AcademicYearWorkloadNorm

        fields = (
            "id",

            "academic_year",
            "academic_year_name",

            "workload_type",
            "workload_type_name",

            "coefficient",

            "is_active",
            "notes",

            "created_at",
            "updated_at",

            "created_by",
            "created_by_name",

            "updated_by",
            "updated_by_name",

            "is_archived",
        )


class AcademicYearCreditNormSerializer(
    AuditFieldsSerializer,
):
    academic_year_name = (
        serializers.CharField(
            source="academic_year.name",
            read_only=True,
        )
    )

    class Meta:
        model = AcademicYearCreditNorm

        fields = (
            "id",

            "academic_year",
            "academic_year_name",

            "hours_per_credit",

            "notes",

            "created_at",
            "updated_at",

            "created_by",
            "created_by_name",

            "updated_by",
            "updated_by_name",

            "is_archived",
        )