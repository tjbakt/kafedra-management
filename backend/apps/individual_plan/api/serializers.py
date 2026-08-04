from rest_framework import serializers

from apps.common.api.serializers import AuditFieldsSerializer
from apps.individual_plan.models import (
    IndividualActivityType,
    IndividualPlan,
    IndividualPlanItem,
    IndividualPlanSection,
    IndividualPlanTeachingWorkload,
)
from drf_spectacular.utils import extend_schema_field

class IndividualPlanSectionSerializer(
    AuditFieldsSerializer
):
    class Meta:
        model = IndividualPlanSection
        fields = (
            "id",
            "code",
            "name_ru",
            "name_uz",
            "is_hourly",
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
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

class IndividualActivityTypeSerializer(
    AuditFieldsSerializer
):
    section_name = serializers.CharField(
        source="section.name_ru",
        read_only=True,
    )

    class Meta:
        model = IndividualActivityType
        fields = (
            "id",
            "section",
            "section_name",
            "code",
            "name_ru",
            "name_uz",
            "default_hours",
            "requires_evidence",
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

class IndividualPlanItemSerializer(
    AuditFieldsSerializer
):
    section_name = serializers.CharField(
        source="section.name_ru",
        read_only=True,
    )
    activity_type_name = serializers.CharField(
        source="activity_type.name_ru",
        read_only=True,
        allow_null=True,
    )
    academic_semester_name = serializers.CharField(
        source="academic_semester.get_season_display",
        read_only=True,
        allow_null=True,
    )
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    confirmed_by_name = serializers.SerializerMethodField()
    is_imported_teaching_workload = serializers.SerializerMethodField()

    class Meta:
        model = IndividualPlanItem
        fields = (
            "id",
            "individual_plan",
            "section",
            "section_name",
            "activity_type",
            "activity_type_name",
            "academic_semester",
            "academic_semester_name",
            "title",
            "description",
            "planned_hours",
            "actual_hours",
            "planned_start_date",
            "planned_end_date",
            "actual_completion_date",
            "expected_result",
            "actual_result",
            "evidence_url",
            "evidence_document",
            "status",
            "status_name",
            "confirmed_at",
            "confirmed_by",
            "confirmed_by_name",
            "teacher_comment",
            "reviewer_comment",
            "sort_order",
            "is_imported_teaching_workload",
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
            "confirmed_at",
            "confirmed_by",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

    @extend_schema_field(
        serializers.CharField(
            allow_null=True,
        )
    )
    def get_confirmed_by_name(self, obj) -> str | None:
        if not obj.confirmed_by:
            return None

        return (
            obj.confirmed_by.get_full_name()
            or obj.confirmed_by.username
        )

    @extend_schema_field(
        serializers.BooleanField()
    )
    def get_is_imported_teaching_workload(self, obj) -> bool:
        return hasattr(obj, "teaching_workload_link")

    def validate(self, attrs):
        instance = self.instance

        plan = attrs.get(
            "individual_plan",
            getattr(instance, "individual_plan", None),
        )
        section = attrs.get(
            "section",
            getattr(instance, "section", None),
        )
        activity_type = attrs.get(
            "activity_type",
            getattr(instance, "activity_type", None),
        )
        academic_semester = attrs.get(
            "academic_semester",
            getattr(instance, "academic_semester", None),
        )

        if (
            section
            and activity_type
            and activity_type.section_id != section.id
        ):
            raise serializers.ValidationError(
                {
                    "activity_type": (
                        "Вид работы не относится "
                        "к выбранному разделу."
                    )
                }
            )

        if (
            plan
            and academic_semester
            and academic_semester.academic_year_id
            != plan.academic_year_id
        ):
            raise serializers.ValidationError(
                {
                    "academic_semester": (
                        "Семестр относится к другому "
                        "учебному году."
                    )
                }
            )

        if (
            instance
            and hasattr(instance, "teaching_workload_link")
        ):
            protected_fields = {
                "individual_plan",
                "section",
                "planned_hours",
            }

            if protected_fields.intersection(attrs):
                raise serializers.ValidationError(
                    {
                        "detail": (
                            "Импортированные учебные часы "
                            "изменяются через распределение нагрузки."
                        )
                    }
                )

        planned_start_date = attrs.get(
            "planned_start_date",
            getattr(
                instance,
                "planned_start_date",
                None,
            ),
        )
        planned_end_date = attrs.get(
            "planned_end_date",
            getattr(
                instance,
                "planned_end_date",
                None,
            ),
        )
        actual_completion_date = attrs.get(
            "actual_completion_date",
            getattr(
                instance,
                "actual_completion_date",
                None,
            ),
        )
        status_value = attrs.get(
            "status",
            getattr(
                instance,
                "status",
                IndividualPlanItem.Status.PLANNED,
            ),
        )
        evidence_url = attrs.get(
            "evidence_url",
            getattr(
                instance,
                "evidence_url",
                "",
            ),
        )
        evidence_document = attrs.get(
            "evidence_document",
            getattr(
                instance,
                "evidence_document",
                "",
            ),
        )

        if (
                planned_start_date
                and planned_end_date
                and planned_end_date < planned_start_date
        ):
            raise serializers.ValidationError(
                {
                    "planned_end_date": (
                        "Дата окончания не может быть "
                        "раньше даты начала."
                    )
                }
            )

        if (
                status_value
                in (
                IndividualPlanItem.Status.COMPLETED,
                IndividualPlanItem.Status.CONFIRMED,
        )
                and not actual_completion_date
        ):
            raise serializers.ValidationError(
                {
                    "actual_completion_date": (
                        "Для выполненного пункта "
                        "необходимо указать дату выполнения."
                    )
                }
            )

        requires_evidence = (
                activity_type
                and activity_type.requires_evidence
        )

        if (
                requires_evidence
                and status_value
                in (
                IndividualPlanItem.Status.COMPLETED,
                IndividualPlanItem.Status.CONFIRMED,
        )
                and not evidence_url
                and not evidence_document
        ):
            raise serializers.ValidationError(
                {
                    "evidence_document": (
                        "Для этого вида работы требуется "
                        "подтверждающий документ или ссылка."
                    )
                }
            )
        return attrs

class IndividualPlanSerializer(AuditFieldsSerializer):
    teacher = serializers.IntegerField(
        source="staff_employment.staff_member_id",
        read_only=True,
    )
    teacher_name = serializers.CharField(read_only=True)
    personnel_number = serializers.CharField(
        source="staff_employment.staff_member.personnel_number",
        read_only=True,
    )
    department = serializers.IntegerField(
        source="staff_employment.department_id",
        read_only=True,
    )
    department_name = serializers.CharField(
        source="staff_employment.department.name_ru",
        read_only=True,
    )
    position_name = serializers.CharField(
        source="staff_employment.position.name_ru",
        read_only=True,
    )
    employment_rate = serializers.DecimalField(
        source="staff_employment.rate",
        max_digits=4,
        decimal_places=2,
        read_only=True,
    )
    academic_year_name = serializers.CharField(
        source="academic_year.name",
        read_only=True,
    )
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    planned_hours = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    actual_hours = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    completion_percent = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        read_only=True,
    )
    items = IndividualPlanItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = IndividualPlan
        fields = (
            "id",
            "staff_employment",
            "teacher",
            "teacher_name",
            "personnel_number",
            "department",
            "department_name",
            "position_name",
            "employment_rate",
            "academic_year",
            "academic_year_name",
            "status",
            "status_name",
            "planned_hours",
            "actual_hours",
            "completion_percent",
            "submitted_at",
            "approved_at",
            "approved_by",
            "closed_at",
            "teacher_notes",
            "reviewer_notes",
            "items",
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
            "status",
            "submitted_at",
            "approved_at",
            "approved_by",
            "closed_at",
            "planned_hours",
            "actual_hours",
            "completion_percent",
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

        staff_employment = attrs.get(
            "staff_employment",
            getattr(
                instance,
                "staff_employment",
                None,
            ),
        )

        academic_year = attrs.get(
            "academic_year",
            getattr(
                instance,
                "academic_year",
                None,
            ),
        )

        if staff_employment:
            if staff_employment.is_archived:
                raise serializers.ValidationError(
                    {
                        "staff_employment": (
                            "Нельзя создать индивидуальный "
                            "план для архивного назначения."
                        )
                    }
                )

            if not staff_employment.is_active:
                raise serializers.ValidationError(
                    {
                        "staff_employment": (
                            "Трудовое назначение неактивно."
                        )
                    }
                )

            if not (
                    staff_employment
                            .position
                            .is_teaching_position
            ):
                raise serializers.ValidationError(
                    {
                        "staff_employment": (
                            "Индивидуальный план доступен "
                            "только для преподавательских "
                            "должностей."
                        )
                    }
                )

        if (
                instance
                and instance.status
                not in (
                IndividualPlan.Status.DRAFT,
                IndividualPlan.Status.RETURNED,
        )
        ):
            editable_fields = {
                "staff_employment",
                "academic_year",
                "teacher_notes",
            }

            if editable_fields.intersection(attrs):
                raise serializers.ValidationError(
                    {
                        "detail": (
                            "Изменять можно только черновой "
                            "или возвращённый план."
                        )
                    }
                )

        return attrs