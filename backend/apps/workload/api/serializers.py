from decimal import Decimal
from rest_framework import serializers
from django.db.models import Sum
from django.utils.translation import get_language

from apps.common.api.serializers import AuditFieldsSerializer
from apps.workload.models import WorkloadDistribution

from apps.workload.services.academic_year_validation_service import (
    AcademicYearWorkloadValidationService,
)
from drf_spectacular.utils import  extend_schema_field
from apps.staff.models import StaffEmployment

class LocalizedNameMixin:
    def get_localized_name(self, obj) -> str:
        request = self.context.get("request")

        if (
            request
            and request.user
            and request.user.is_authenticated
        ):
            language = getattr(
                request.user,
                "interface_language",
                "ru",
            )
        else:
            language = (get_language() or "ru")[:2]

        if language == "uz":
            return (
                getattr(obj, "name_uz", "")
                or getattr(obj, "name_ru", "")
            )

        return (
            getattr(obj, "name_ru", "")
            or getattr(obj, "name_uz", "")
        )

class WorkloadDistributionValidationMixin:
    """
    Общая бизнес-валидация создания и изменения
    распределения учебной нагрузки.
    """

    def validate_distribution_status(
        self,
        attrs,
    ):
        instance = self.instance

        if instance is None:
            return

        if (
            instance.status
            == WorkloadDistribution.Status.APPROVED
        ):
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Утверждённое распределение "
                        "нельзя изменять. Сначала "
                        "верните его в черновик."
                    )
                }
            )

        if (
            instance.status
            == WorkloadDistribution.Status.CANCELLED
        ):
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Отменённое распределение "
                        "нельзя изменять."
                    )
                }
            )

    def validate_distribution_data(
        self,
        attrs,
    ):
        instance = self.instance

        planned_workload = attrs.get(
            "planned_workload",
            getattr(
                instance,
                "planned_workload",
                None,
            ),
        )
        staff_employment = attrs.get(
            "staff_employment",
            getattr(
                instance,
                "staff_employment",
                None,
            ),
        )
        allocated_hours = attrs.get(
            "allocated_hours",
            getattr(
                instance,
                "allocated_hours",
                None,
            ),
        )

        if planned_workload and staff_employment:
            if (
                planned_workload
                .teaching_department_id
                != staff_employment.department_id
            ):
                raise serializers.ValidationError(
                    {
                        "staff_employment": (
                            "Трудовое назначение "
                            "преподавателя должно "
                            "относиться к обеспечивающей "
                            "кафедре."
                        )
                    }
                )

            if (
                staff_employment.is_archived
                or not staff_employment.is_active
            ):
                raise serializers.ValidationError(
                    {
                        "staff_employment": (
                            "Трудовое назначение "
                            "неактивно или архивировано."
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
                            "Должность сотрудника "
                            "не участвует в учебной "
                            "нагрузке."
                        )
                    }
                )

            academic_year_record = (
                staff_employment
                .get_academic_year_record(
                    planned_workload.academic_year
                )
            )

            if (
                academic_year_record is None
                or not academic_year_record.is_active
                or academic_year_record.is_archived
            ):
                raise serializers.ValidationError(
                    {
                        "staff_employment": (
                            "Для трудового назначения "
                            "отсутствует активная "
                            "кадровая запись на выбранный "
                            "учебный год."
                        )
                    }
                )

        if (
            planned_workload
            and allocated_hours is not None
        ):
            distributions = (
                WorkloadDistribution.objects
                .filter(
                    planned_workload=(
                        planned_workload
                    ),
                    status__in=(
                        WorkloadDistribution
                        .Status
                        .DRAFT,
                        WorkloadDistribution
                        .Status
                        .APPROVED,
                    ),
                    is_archived=False,
                )
            )

            if instance is not None:
                distributions = (
                    distributions.exclude(
                        pk=instance.pk
                    )
                )

            distributed_hours = (
                distributions.aggregate(
                    total=Sum(
                        "allocated_hours"
                    )
                )["total"]
                or Decimal("0.00")
            )

            remaining_hours = (
                planned_workload.total_hours
                - distributed_hours
            )

            if allocated_hours > remaining_hours:
                raise serializers.ValidationError(
                    {
                        "allocated_hours": (
                            "Доступный остаток "
                            "нагрузки: "
                            f"{remaining_hours} часов."
                        )
                    }
                )

    def validate(self, attrs):
        attrs = super().validate(attrs)

        self.validate_distribution_status(
            attrs
        )
        self.validate_distribution_data(
            attrs
        )

        return attrs

class WorkloadDistributionSerializer(
    LocalizedNameMixin,
    AuditFieldsSerializer,
    WorkloadDistributionValidationMixin,
):
    teacher = serializers.IntegerField(
        source="staff_employment.staff_member_id",
        read_only=True,
    )
    teacher_name = serializers.CharField(
        source="staff_employment.staff_member.full_name",
        read_only=True,
    )
    personnel_number = serializers.CharField(
        source=(
            "staff_employment.staff_member.personnel_number"
        ),
        read_only=True,
    )

    employment_rate = serializers.DecimalField(
        source="staff_employment.rate",
        max_digits=4,
        decimal_places=2,
        read_only=True,
    )
    employment_type = serializers.CharField(
        source="staff_employment.employment_type",
        read_only=True,
    )

    position_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    academic_year_name = serializers.CharField(
        source="planned_workload.academic_year.name",
        read_only=True,
    )
    academic_semester_name = serializers.CharField(
        source=(
            "planned_workload.academic_semester."
            "get_season_display"
        ),
        read_only=True,
    )
    stream_code = serializers.CharField(
        source="planned_workload.teaching_stream.code",
        read_only=True,
    )
    semester_number = serializers.IntegerField(
        source=(
            "planned_workload."
            "teaching_stream."
            "semester_number"
        ),
        read_only=True,
    )

    season = serializers.CharField(
        source=(
            "planned_workload."
            "teaching_stream."
            "season"
        ),
        read_only=True,
    )

    group_semester = serializers.IntegerField(
        source=(
            "planned_workload."
            "group_semester_id"
        ),
        read_only=True,
        allow_null=True,
    )

    student_group = serializers.IntegerField(
        source=(
            "planned_workload."
            "group_semester."
            "group_curriculum."
            "student_group_id"
        ),
        read_only=True,
        allow_null=True,
    )

    student_group_code = serializers.CharField(
        source=(
            "planned_workload."
            "group_semester."
            "group_curriculum."
            "student_group."
            "code"
        ),
        read_only=True,
        allow_null=True,
    )

    workload_scope = (
        serializers.SerializerMethodField()
    )
    discipline_name = serializers.SerializerMethodField()
    workload_type_name = serializers.SerializerMethodField()
    planned_total_hours = serializers.DecimalField(
        source="planned_workload.total_hours",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    approved_by_name = serializers.SerializerMethodField()

    curriculum = serializers.IntegerField(
        source="planned_workload.teaching_stream.curriculum_id",
        read_only=True,
    )

    curriculum_code = serializers.CharField(
        source="planned_workload.teaching_stream.curriculum.code",
        read_only=True,
    )

    discipline_code = serializers.CharField(
        source=(
            "planned_workload.curriculum_workload."
            "curriculum_discipline.discipline.code"
        ),
        read_only=True,
    )

    planned_remaining_hours = serializers.DecimalField(
        source="planned_workload.remaining_hours",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    @extend_schema_field(
        serializers.ChoiceField(
            choices=(
                    "stream",
                    "group",
            )
        )
    )
    def get_workload_scope(
            self,
            obj,
    ) -> str:
        if (
                obj.planned_workload
                        .group_semester_id
                is None
        ):
            return "stream"

        return "group"

    @extend_schema_field(serializers.CharField())
    def get_position_name(self, obj) -> str:
        return self.get_localized_name(
            obj.staff_employment.position
        )

    @extend_schema_field(serializers.CharField())
    def get_department_name(self, obj) -> str:
        return self.get_localized_name(
            obj.planned_workload.teaching_department
        )

    @extend_schema_field(serializers.CharField())
    def get_discipline_name(self, obj) -> str:
        return self.get_localized_name(
            obj.planned_workload
            .curriculum_workload
            .curriculum_discipline
            .discipline
        )

    @extend_schema_field(serializers.CharField())
    def get_workload_type_name(self, obj) -> str:
        return self.get_localized_name(
            obj.planned_workload
            .curriculum_workload
            .workload_type
        )

    class Meta:
        model = WorkloadDistribution
        fields = (
            "id",
            "planned_workload",
            "planned_remaining_hours",
            "curriculum",
            "curriculum_code",
            "discipline_code",
            "planned_total_hours",
            "stream_code",
            "semester_number",
            "season",
            "group_semester",
            "student_group",
            "student_group_code",
            "workload_scope",
            "discipline_name",
            "workload_type_name",
            "department_name",
            "academic_year_name",
            "academic_semester_name",
            "staff_employment",
            "teacher",
            "teacher_name",
            "personnel_number",
            "position_name",
            "employment_rate",
            "employment_type",
            "allocated_hours",
            "status",
            "status_name",
            "approved_at",
            "approved_by",
            "approved_by_name",
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
            "status",
            "approved_at",
            "approved_by",
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
    def get_approved_by_name(self, obj) -> str | None:
        if not obj.approved_by:
            return None

        if hasattr(obj.approved_by, "get_full_name"):
            return (
                obj.approved_by.get_full_name()
                or obj.approved_by.username
            )

        return str(obj.approved_by)

class WorkloadDistributionCreateSerializer(
    WorkloadDistributionValidationMixin,
    serializers.ModelSerializer
):
    """
    Создание распределения учебной нагрузки.
    """

    class Meta:
        model = WorkloadDistribution
        fields = (
            "planned_workload",
            "staff_employment",
            "allocated_hours",
            "notes",
        )
        extra_kwargs = {
            "planned_workload": {
                "required": True,
                "help_text": (
                    "ID плановой учебной нагрузки."
                ),
            },
            "staff_employment": {
                "required": True,
                "help_text": (
                    "ID трудового назначения "
                    "преподавателя."
                ),
            },
            "allocated_hours": {
                "required": True,
                "help_text": (
                    "Количество часов, распределяемых "
                    "преподавателю."
                ),
            },
            "notes": {
                "required": False,
                "allow_blank": True,
                "help_text": (
                    "Необязательное примечание "
                    "к распределению."
                ),
            },
        }


class WorkloadDistributionUpdateSerializer(
    WorkloadDistributionValidationMixin,
    serializers.ModelSerializer
):
    """
    Полное изменение распределения нагрузки.

    Плановая нагрузка после создания не изменяется.
    """

    class Meta:
        model = WorkloadDistribution
        fields = (
            "staff_employment",
            "allocated_hours",
            "notes",
        )
        extra_kwargs = {
            "staff_employment": {
                "required": True,
                "help_text": (
                    "ID трудового назначения "
                    "преподавателя."
                ),
            },
            "allocated_hours": {
                "required": True,
                "help_text": (
                    "Новое количество распределённых "
                    "часов."
                ),
            },
            "notes": {
                "required": False,
                "allow_blank": True,
                "help_text": (
                    "Примечание к распределению."
                ),
            },
        }


class WorkloadDistributionPartialUpdateSerializer(
    WorkloadDistributionValidationMixin,
    serializers.ModelSerializer
):
    """
    Частичное изменение распределения нагрузки.
    """

    class Meta:
        model = WorkloadDistribution
        fields = (
            "staff_employment",
            "allocated_hours",
            "notes",
        )
        extra_kwargs = {
            "staff_employment": {
                "required": False,
                "help_text": (
                    "Новое трудовое назначение "
                    "преподавателя."
                ),
            },
            "allocated_hours": {
                "required": False,
                "help_text": (
                    "Новое количество распределённых "
                    "часов."
                ),
            },
            "notes": {
                "required": False,
                "allow_blank": True,
                "help_text": (
                    "Новое примечание."
                ),
            },
        }


class WorkloadDistributionArchiveRestoreResponseSerializer(
    serializers.Serializer
):
    """
    Результат восстановления распределения из архива.
    """

    detail = serializers.CharField()
    data = WorkloadDistributionSerializer()

class TeacherWorkloadSummarySerializer(
    serializers.Serializer
):
    staff_employment_academic_year = (
        serializers.IntegerField()
    )
    staff_employment = serializers.IntegerField()
    staff_member = serializers.IntegerField()
    teacher_name = serializers.CharField()
    personnel_number = serializers.CharField()

    department = serializers.IntegerField()
    department_name = serializers.CharField()

    position = serializers.IntegerField()
    position_name = serializers.CharField()

    academic_year = serializers.IntegerField()
    academic_year_name = serializers.CharField()

    employment_rate = serializers.DecimalField(
        max_digits=4,
        decimal_places=2,
    )
    has_academic_degree = serializers.BooleanField()
    has_academic_title = serializers.BooleanField()

    recommended_hours = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        allow_null=True,
    )
    distributed_hours = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    remaining_hours = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        allow_null=True,
    )
    difference_hours = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        allow_null=True,
    )
    load_percent = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        allow_null=True,
    )
    load_status = serializers.ChoiceField(
        choices=(
            "underloaded",
            "balanced",
            "overloaded",
            "norm_missing",
        )
    )
    norm_found = serializers.BooleanField()

class DepartmentWorkloadSummarySerializer(
    serializers.Serializer
):
    department = serializers.IntegerField()
    department_name = serializers.CharField()

    academic_year = serializers.IntegerField()
    academic_year_name = serializers.CharField()

    planned_positions = serializers.IntegerField()

    planned_hours = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    draft_hours = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    approved_hours = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    distributed_hours = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    remaining_hours = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    distribution_percent = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
    )
    distribution_status = serializers.ChoiceField(
        choices=(
            "incomplete",
            "complete",
            "exceeded",
        )
    )

class WorkloadDashboardTotalsSerializer(
    serializers.Serializer
):
    planned_positions = serializers.IntegerField()

    planned_hours = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    draft_hours = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    approved_hours = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    distributed_hours = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    remaining_hours = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    distribution_percent = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
    )


class WorkloadDashboardTeachersSerializer(
    serializers.Serializer
):
    total = serializers.IntegerField()
    with_norm = serializers.IntegerField()
    without_norm = serializers.IntegerField()
    underloaded = serializers.IntegerField()
    balanced = serializers.IntegerField()
    overloaded = serializers.IntegerField()

    recommended_hours = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    distributed_hours = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )


class WorkloadDashboardDepartmentsSerializer(
    serializers.Serializer
):
    total = serializers.IntegerField()
    incomplete = serializers.IntegerField()
    complete = serializers.IntegerField()
    exceeded = serializers.IntegerField()


class WorkloadDashboardSerializer(
    serializers.Serializer
):
    academic_year = serializers.IntegerField()
    academic_year_name = serializers.CharField()

    department = serializers.IntegerField(
        allow_null=True,
    )

    workload = WorkloadDashboardTotalsSerializer()
    teachers = WorkloadDashboardTeachersSerializer()
    departments = (
        WorkloadDashboardDepartmentsSerializer()
    )

class TeacherWorkloadSummaryQuerySerializer(
    serializers.Serializer
):
    """
    Параметры сводки нагрузки преподавателей.
    """

    academic_year = serializers.IntegerField(
        min_value=1,
        required=True,
        help_text="ID учебного года.",
    )

    staff_member = serializers.IntegerField(
        min_value=1,
        required=False,
        help_text=(
            "ID преподавателя. Если не указан, "
            "возвращаются все доступные преподаватели."
        ),
    )

    department = serializers.IntegerField(
        min_value=1,
        required=False,
        help_text=(
            "ID кафедры для фильтрации преподавателей."
        ),
    )


class DepartmentWorkloadSummaryQuerySerializer(
    serializers.Serializer
):
    """
    Параметры сводки нагрузки кафедр.
    """

    academic_year = serializers.IntegerField(
        min_value=1,
        required=True,
        help_text="ID учебного года.",
    )

    academic_semester = serializers.IntegerField(
        min_value=1,
        required=False,
        help_text=(
            "ID семестра учебного года."
        ),
    )

    department = serializers.IntegerField(
        min_value=1,
        required=False,
        help_text=(
            "ID кафедры. Если не указан, "
            "возвращаются все доступные кафедры."
        ),
    )


class WorkloadDashboardQuerySerializer(
    serializers.Serializer
):
    """
    Параметры dashboard учебной нагрузки.
    """

    academic_year = serializers.IntegerField(
        min_value=1,
        required=True,
        help_text="ID учебного года.",
    )

    department = serializers.IntegerField(
        min_value=1,
        required=False,
        help_text=(
            "ID кафедры. Если не указан, dashboard "
            "строится по всей доступной области."
        ),
    )

class ApproveSelectedDistributionsSerializer(
    serializers.Serializer
):
    """
    Запрос на массовое утверждение распределений.
    """

    ids = serializers.ListField(
        child=serializers.IntegerField(
            min_value=1,
        ),
        allow_empty=False,
        max_length=500,
        help_text=(
            "Список ID распределений нагрузки. "
            "Повторяющиеся ID будут удалены."
        ),
    )

    def validate_ids(
        self,
        value,
    ):
        return list(
            dict.fromkeys(value)
        )

class BulkDistributionErrorSerializer(
    serializers.Serializer
):
    id = serializers.IntegerField()
    error = serializers.JSONField()

class ApproveSelectedDistributionsResultSerializer(
    serializers.Serializer
):
    """
    Результат массового утверждения.
    """

    requested_count = serializers.IntegerField(
        min_value=0,
    )
    found_count = serializers.IntegerField(
        min_value=0,
    )

    approved_count = serializers.IntegerField(
        min_value=0,
    )
    approved_ids = serializers.ListField(
        child=serializers.IntegerField(),
    )

    unavailable_count = serializers.IntegerField(
        min_value=0,
    )
    unavailable_ids = serializers.ListField(
        child=serializers.IntegerField(),
    )

    errors_count = serializers.IntegerField(
        min_value=0,
    )
    errors = BulkDistributionErrorSerializer(
        many=True,
    )

class CancelSelectedDistributionsSerializer(
    serializers.Serializer
):
    ids = serializers.ListField(
        child=serializers.IntegerField(
            min_value=1,
        ),
        allow_empty=False,
        max_length=500,
        help_text=(
            "Список ID распределений для отмены."
        ),
    )

    reason = serializers.CharField(
        max_length=1000,
        allow_blank=False,
        trim_whitespace=True,
        help_text=(
            "Общая причина отмены распределений."
        ),
    )

    def validate_ids(self, value):
        """
        Удаляет повторяющиеся ID, сохраняя их порядок.
        """

        return list(dict.fromkeys(value))

    def validate_reason(self, value):
        normalized_value = value.strip()

        if not normalized_value:
            raise serializers.ValidationError(
                "Укажите причину массовой отмены."
            )

        return normalized_value


class CancelSelectedDistributionsResultSerializer(
    serializers.Serializer
):
    requested_count = serializers.IntegerField()
    found_count = serializers.IntegerField()

    cancelled_count = serializers.IntegerField()
    cancelled_ids = serializers.ListField(
        child=serializers.IntegerField(),
    )

    unavailable_count = serializers.IntegerField()
    unavailable_ids = serializers.ListField(
        child=serializers.IntegerField(),
    )

    errors_count = serializers.IntegerField()
    errors = BulkDistributionErrorSerializer(
        many=True,
    )

class RestoreDistributionSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        max_length=1000,
        allow_blank=False,
        trim_whitespace=True,
    )

    def validate_reason(self, value):
        normalized_value = value.strip()

        if not normalized_value:
            raise serializers.ValidationError(
                "Укажите причину восстановления."
            )

        return normalized_value

class RestoreSelectedDistributionsSerializer(
    serializers.Serializer
):
    ids = serializers.ListField(
        child=serializers.IntegerField(
            min_value=1,
        ),
        allow_empty=False,
        max_length=500,
        help_text=(
            "Список ID распределений для восстановления."
        ),
    )

    reason = serializers.CharField(
        max_length=1000,
        allow_blank=False,
        trim_whitespace=True,
        help_text=(
            "Общая причина восстановления."
        ),
    )

    def validate_ids(self, value):
        return list(dict.fromkeys(value))

    def validate_reason(self, value):
        normalized_value = value.strip()

        if not normalized_value:
            raise serializers.ValidationError(
                "Укажите причину массового "
                "восстановления."
            )

        return normalized_value

class RestoreSelectedDistributionsResultSerializer(
    serializers.Serializer
):
    requested_count = serializers.IntegerField()
    found_count = serializers.IntegerField()

    restored_count = serializers.IntegerField()
    restored_ids = serializers.ListField(
        child=serializers.IntegerField(),
    )

    unavailable_count = serializers.IntegerField()
    unavailable_ids = serializers.ListField(
        child=serializers.IntegerField(),
    )

    errors_count = serializers.IntegerField()
    errors = BulkDistributionErrorSerializer(
        many=True,
    )

class TransferDistributionHoursSerializer(
    serializers.Serializer
):
    target_staff_employment = (
        serializers.IntegerField(
            min_value=1,
        )
    )

    transfer_hours = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    reason = serializers.CharField(
        max_length=1000,
        allow_blank=False,
        trim_whitespace=True,
    )

    def validate_reason(self, value):
        normalized_value = value.strip()

        if not normalized_value:
            raise serializers.ValidationError(
                "Укажите причину переноса часов."
            )

        return normalized_value

class TransferDistributionHoursResultSerializer(
    serializers.Serializer
):
    transferred_hours = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    source_cancelled = serializers.BooleanField()
    target_created = serializers.BooleanField()

    source_distribution = (
        WorkloadDistributionSerializer()
    )
    target_distribution = (
        WorkloadDistributionSerializer()
    )

class ReturnDistributionToDraftSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        max_length=1000,
        allow_blank=False,
        trim_whitespace=True,
    )

    def validate_reason(self, value):
        normalized_value = value.strip()

        if not normalized_value:
            raise serializers.ValidationError(
                "Укажите причину возврата "
                "распределения в черновик."
            )

        return normalized_value

class ReturnSelectedToDraftSerializer(
    serializers.Serializer
):
    ids = serializers.ListField(
        child=serializers.IntegerField(
            min_value=1,
        ),
        allow_empty=False,
        max_length=500,
        help_text=(
            "Список ID распределений для возврата в статус черновика."
        ),
    )

    reason = serializers.CharField(
        max_length=1000,
        allow_blank=False,
        trim_whitespace=True,
        help_text=(
            "Общая причина возврата в черновик."
        ),
    )

    def validate_ids(self, value):
        return list(dict.fromkeys(value))

    def validate_reason(self, value):
        normalized_value = value.strip()

        if not normalized_value:
            raise serializers.ValidationError(
                "Укажите причину массового "
                "возврата в черновик."
            )

        return normalized_value

class ReturnSelectedToDraftResultSerializer(
    serializers.Serializer
):
    requested_count = serializers.IntegerField()
    found_count = serializers.IntegerField()

    returned_count = serializers.IntegerField()
    returned_ids = serializers.ListField(
        child=serializers.IntegerField(),
    )

    unavailable_count = serializers.IntegerField()
    unavailable_ids = serializers.ListField(
        child=serializers.IntegerField(),
    )

    errors_count = serializers.IntegerField()
    errors = BulkDistributionErrorSerializer(
        many=True,
    )

class DistributionActionAvailabilitySerializer(
    serializers.Serializer
):
    allowed = serializers.BooleanField()
    reason = serializers.CharField(
        allow_blank=True,
    )

class DistributionActionsSerializer(
    serializers.Serializer
):
    approve = (
        DistributionActionAvailabilitySerializer()
    )
    return_to_draft = (
        DistributionActionAvailabilitySerializer()
    )
    cancel = (
        DistributionActionAvailabilitySerializer()
    )
    restore = (
        DistributionActionAvailabilitySerializer()
    )
    transfer = (
        DistributionActionAvailabilitySerializer()
    )
    edit = (
        DistributionActionAvailabilitySerializer()
    )

class DistributionAvailableActionsSerializer(
    serializers.Serializer
):
    distribution_id = serializers.IntegerField()
    status = serializers.CharField()
    status_label = serializers.CharField()

    actions = DistributionActionsSerializer()

class AcademicYearValidationQuerySerializer(
    serializers.Serializer
):
    """
    Параметры проверки нагрузки учебного года.
    """

    academic_year = serializers.IntegerField(
        min_value=1,
        required=True,
        help_text="ID учебного года.",
    )

    department = serializers.IntegerField(
        min_value=1,
        required=False,
        help_text=(
            "ID кафедры. Если параметр не указан, "
            "проверяются все кафедры, доступные "
            "текущему пользователю."
        ),
    )

    severity = serializers.ChoiceField(
        choices=(
            AcademicYearWorkloadValidationService
            .Severity.CHOICES
        ),
        required=False,
        help_text=(
            "Фильтр проблем по уровню серьёзности."
        ),
    )

    issue_type = serializers.ChoiceField(
        choices=(
            AcademicYearWorkloadValidationService
            .IssueType.CHOICES
        ),
        required=False,
        help_text=(
            "Фильтр по типу обнаруженной проблемы."
        ),
    )

class AcademicYearValidationIssueSerializer(
    serializers.Serializer
):
    severity = serializers.ChoiceField(
        choices=(
            AcademicYearWorkloadValidationService
            .Severity.CHOICES
        )
    )
    issue_type = serializers.ChoiceField(
        choices=(
            AcademicYearWorkloadValidationService
            .IssueType.CHOICES
        )
    )
    message = serializers.CharField()

    department_id = serializers.IntegerField()
    department_name = serializers.CharField()

    staff_employment_id = serializers.IntegerField(
        allow_null=True,
    )
    staff_member_id = serializers.IntegerField(
        allow_null=True,
    )
    teacher_name = serializers.CharField(
        allow_null=True,
    )

    planned_workload_id = serializers.IntegerField(
        allow_null=True,
    )
    distribution_id = serializers.IntegerField(
        allow_null=True,
    )

    stream_code = serializers.CharField(
        allow_null=True,
        required=False,
    )
    discipline_name = serializers.CharField(
        allow_null=True,
        required=False,
    )
    workload_type_name = serializers.CharField(
        allow_null=True,
        required=False,
    )

    details = serializers.JSONField()


class AcademicYearValidationSummarySerializer(
    serializers.Serializer
):
    planned_workloads_count = serializers.IntegerField()
    distributions_count = serializers.IntegerField()
    year_staff_records_count = serializers.IntegerField()

    issues_count = serializers.IntegerField()
    errors_count = serializers.IntegerField()
    warnings_count = serializers.IntegerField()

    issues_by_type = serializers.DictField(
        child=serializers.IntegerField(),
    )


class AcademicYearValidationResultSerializer(
    serializers.Serializer
):
    academic_year = serializers.IntegerField()
    academic_year_name = serializers.CharField()

    department_ids = serializers.ListField(
        child=serializers.IntegerField(),
    )

    is_valid = serializers.BooleanField()

    summary = (
        AcademicYearValidationSummarySerializer()
    )
    issues = AcademicYearValidationIssueSerializer(
        many=True,
    )

class AcademicYearClosingReadinessQuerySerializer(
    serializers.Serializer
):
    """
    Параметры проверки готовности учебного года
    к закрытию.
    """

    academic_year = serializers.IntegerField(
        min_value=1,
        required=True,
        help_text="ID учебного года.",
    )

    department = serializers.IntegerField(
        min_value=1,
        required=False,
        help_text=(
            "ID кафедры. Если параметр не указан, "
            "проверяются все кафедры, доступные "
            "текущему пользователю."
        ),
    )

class AcademicYearClosingReadinessSummarySerializer(
    serializers.Serializer
):
    planned_workloads_count = serializers.IntegerField()
    distributions_count = serializers.IntegerField()
    year_staff_records_count = serializers.IntegerField()

    blocking_issues_count = serializers.IntegerField()
    warnings_count = serializers.IntegerField()

    blocking_issues_by_type = serializers.DictField(
        child=serializers.IntegerField(),
    )
    warnings_by_type = serializers.DictField(
        child=serializers.IntegerField(),
    )

class AcademicYearClosingReadinessResultSerializer(
    serializers.Serializer
):
    academic_year = serializers.IntegerField()
    academic_year_name = serializers.CharField()

    department_ids = serializers.ListField(
        child=serializers.IntegerField(),
    )

    ready_to_close = serializers.BooleanField()

    status = serializers.ChoiceField(
        choices=(
            "ready",
            "not_ready",
        )
    )

    message = serializers.CharField()

    summary = (
        AcademicYearClosingReadinessSummarySerializer()
    )

    blocking_issues = (
        AcademicYearValidationIssueSerializer(
            many=True,
        )
    )

    warnings = AcademicYearValidationIssueSerializer(
        many=True,
    )

class CancelDistributionSerializer(
    serializers.Serializer
):
    """
    Запрос на отмену распределения нагрузки.
    """

    reason = serializers.CharField(
        max_length=1000,
        allow_blank=False,
        trim_whitespace=True,
        help_text=(
            "Причина отмены распределения."
        ),
    )

    def validate_reason(
        self,
        value,
    ):
        normalized_value = value.strip()

        if not normalized_value:
            raise serializers.ValidationError(
                "Укажите причину отмены "
                "распределения."
            )

        return normalized_value


class WorkloadDistributionActionResponseSerializer(
    serializers.Serializer
):
    """
    Результат изменения состояния распределения.
    """

    detail = serializers.CharField()
    data = WorkloadDistributionSerializer()


class TransferDistributionActionResponseSerializer(
    serializers.Serializer
):
    """
    Результат переноса часов нагрузки.
    """

    detail = serializers.CharField()
    data = (
        TransferDistributionHoursResultSerializer()
    )

class AssignSelectedPlannedWorkloadsSerializer(
    serializers.Serializer
):
    """
    Массовое назначение нескольких позиций
    плановой нагрузки одному преподавателю.

    Для каждой позиции назначается весь
    доступный на момент операции остаток часов.
    """

    planned_workloads = serializers.ListField(
        child=serializers.IntegerField(
            min_value=1,
        ),
        allow_empty=False,
        max_length=500,
        help_text=(
            "Список ID позиций плановой нагрузки."
        ),
    )

    staff_employment = (
        serializers.PrimaryKeyRelatedField(
            queryset=(
                StaffEmployment.objects
                .filter(
                    is_archived=False,
                )
                .select_related(
                    "staff_member",
                    "department",
                    "position",
                )
            ),
            help_text=(
                "Трудовое назначение преподавателя."
            ),
        )
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
        trim_whitespace=True,
        help_text=(
            "Общее примечание ко всем "
            "создаваемым распределениям."
        ),
    )

    def validate_planned_workloads(
        self,
        value,
    ):
        return list(
            dict.fromkeys(value)
        )


class AssignSelectedPlannedWorkloadErrorSerializer(
    serializers.Serializer
):
    planned_workload = (
        serializers.IntegerField()
    )

    error = serializers.JSONField()


class AssignSelectedPlannedWorkloadsResultSerializer(
    serializers.Serializer
):
    requested_count = serializers.IntegerField()

    found_count = serializers.IntegerField()

    created_count = serializers.IntegerField()

    created_ids = serializers.ListField(
        child=serializers.IntegerField(),
    )

    unavailable_count = serializers.IntegerField()

    unavailable_ids = serializers.ListField(
        child=serializers.IntegerField(),
    )

    errors_count = serializers.IntegerField()

    errors = (
        AssignSelectedPlannedWorkloadErrorSerializer(
            many=True,
        )
    )

    allocated_hours = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )