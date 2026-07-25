from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers

from apps.common.api.serializers import AuditFieldsSerializer
from apps.staff.models import WorkloadNorm
from apps.workload.models import WorkloadDistribution

class WorkloadDistributionSerializer(
    AuditFieldsSerializer
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
    employment_type = serializers.CharField(
        source="staff_employment.employment_type",
        read_only=True,
    )
    department_name = serializers.CharField(
        source="planned_workload.teaching_department.name_ru",
        read_only=True,
    )
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
    discipline_name = serializers.CharField(
        source=(
            "planned_workload.teaching_stream."
            "curriculum_discipline.discipline.name_ru"
        ),
        read_only=True,
    )
    workload_type_name = serializers.CharField(
        source=(
            "planned_workload.curriculum_workload."
            "workload_type.name_ru"
        ),
        read_only=True,
    )
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

    class Meta:
        model = WorkloadDistribution
        fields = (
            "id",
            "planned_workload",
            "planned_total_hours",
            "stream_code",
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

    def get_approved_by_name(self, obj):
        if not obj.approved_by:
            return None

        if hasattr(obj.approved_by, "get_full_name"):
            return (
                obj.approved_by.get_full_name()
                or obj.approved_by.username
            )

        return str(obj.approved_by)

    def validate(self, attrs):
        instance = self.instance

        planned_workload = attrs.get(
            "planned_workload",
            getattr(instance, "planned_workload", None),
        )
        staff_employment = attrs.get(
            "staff_employment",
            getattr(instance, "staff_employment", None),
        )
        allocated_hours = attrs.get(
            "allocated_hours",
            getattr(instance, "allocated_hours", None),
        )

        if planned_workload and staff_employment:
            if (
                planned_workload.teaching_department_id
                != staff_employment.department_id
            ):
                raise serializers.ValidationError(
                    {
                        "staff_employment": (
                            "Трудовое назначение преподавателя "
                            "должно относиться к обеспечивающей кафедре."
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

            if not staff_employment.position.is_teaching_position:
                raise serializers.ValidationError(
                    {
                        "staff_employment": (
                            "Должность сотрудника не участвует "
                            "в учебной нагрузке."
                        )
                    }
                )

        if (
            instance
            and instance.status
            == WorkloadDistribution.Status.APPROVED
        ):
            changed_fields = {
                field
                for field in (
                    "planned_workload",
                    "staff_employment",
                    "allocated_hours",
                )
                if field in attrs
                and attrs[field] != getattr(instance, field)
            }

            if changed_fields:
                raise serializers.ValidationError(
                    {
                        "detail": (
                            "Утверждённое распределение нельзя "
                            "изменять."
                        )
                    }
                )

        if planned_workload and allocated_hours:
            other_distributed = (
                WorkloadDistribution.objects
                .filter(
                    planned_workload=planned_workload,
                    status__in=(
                        WorkloadDistribution.Status.DRAFT,
                        WorkloadDistribution.Status.APPROVED,
                    ),
                )
                .exclude(
                    pk=instance.pk if instance else None
                )
                .aggregate(
                    total=Sum("allocated_hours")
                )["total"]
                or Decimal("0.00")
            )

            remaining = (
                planned_workload.total_hours
                - other_distributed
            )

            if allocated_hours > remaining:
                raise serializers.ValidationError(
                    {
                        "allocated_hours": (
                            "Доступный остаток нагрузки: "
                            f"{remaining} часов."
                        )
                    }
                )

        return attrs

class TeacherWorkloadSummarySerializer(
    serializers.Serializer
):
    staff_member = serializers.IntegerField()
    teacher_name = serializers.CharField()
    personnel_number = serializers.CharField()
    academic_year = serializers.IntegerField()
    academic_year_name = serializers.CharField()
    employment_rate = serializers.DecimalField(
        max_digits=4,
        decimal_places=2,
    )
    recommended_hours = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        allow_null=True,
    )
    distributed_hours = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
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
    norm_found = serializers.BooleanField()