from rest_framework import serializers

from apps.academics.models import AcademicYear
from apps.organizations.models import Department
from apps.staff.models import StaffEmployment


class TeacherWorkloadReportRequestSerializer(
    serializers.Serializer
):
    staff_employment = serializers.PrimaryKeyRelatedField(
        queryset=StaffEmployment.objects.filter(
            is_archived=False,
            is_active=True,
        ).select_related(
            "staff_member",
            "department",
            "position",
        ),
    )
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.filter(
            is_archived=False,
        ),
    )

    def validate_staff_employment(self, value):
        if not value.is_active:
            raise serializers.ValidationError(
                "Назначение сотрудника неактивно."
            )

        if not value.position.is_teaching_position:
            raise serializers.ValidationError(
                "Выбранное назначение не является преподавательским."
            )

        return value


class DepartmentWorkloadReportRequestSerializer(
    serializers.Serializer
):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(
            is_archived=False,
        ),
    )
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.filter(
            is_archived=False,
        ),
    )