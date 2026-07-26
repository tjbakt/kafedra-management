from django.utils.translation import get_language
from rest_framework import serializers

from apps.common.api.serializers import AuditFieldsSerializer
from apps.staff.models import (
    AcademicDegree,
    AcademicTitle,
    StaffEmployment,
    StaffEmploymentAcademicYear,
    StaffMember,
    StaffPosition,
    WorkloadNorm,
)
from apps.academics.models import AcademicYear
from apps.organizations.models import Department


class LocalizedStaffNameMixin:
    display_name = serializers.SerializerMethodField()

    def get_display_name(self, obj):
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


class StaffPositionSerializer(
    LocalizedStaffNameMixin,
    AuditFieldsSerializer,
):
    category_name = serializers.CharField(
        source="get_category_display",
        read_only=True,
    )

    class Meta:
        model = StaffPosition
        fields = (
            "id",
            "code",
            "name_ru",
            "name_uz",
            "display_name",
            "category",
            "category_name",
            "is_teaching_position",
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


class AcademicDegreeSerializer(
    LocalizedStaffNameMixin,
    AuditFieldsSerializer,
):
    class Meta:
        model = AcademicDegree
        fields = (
            "id",
            "code",
            "name_ru",
            "name_uz",
            "short_name_ru",
            "short_name_uz",
            "display_name",
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


class AcademicTitleSerializer(
    LocalizedStaffNameMixin,
    AuditFieldsSerializer,
):
    class Meta:
        model = AcademicTitle
        fields = (
            "id",
            "code",
            "name_ru",
            "name_uz",
            "short_name_ru",
            "short_name_uz",
            "display_name",
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

class StaffEmploymentShortSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department.name_ru",
        read_only=True,
    )
    position_name = serializers.CharField(
        source="position.name_ru",
        read_only=True,
    )
    employment_type_name = serializers.CharField(
        source="get_employment_type_display",
        read_only=True,
    )

    class Meta:
        model = StaffEmployment
        fields = (
            "id",
            "department",
            "department_name",
            "position",
            "position_name",
            "employment_type",
            "employment_type_name",
            "rate",
            "start_date",
            "end_date",
            "is_primary",
            "is_active",
        )


class StaffMemberSerializer(AuditFieldsSerializer):
    full_name = serializers.CharField(read_only=True)
    has_academic_degree = serializers.BooleanField(read_only=True)
    has_academic_title = serializers.BooleanField(read_only=True)
    username = serializers.CharField(
        source="user.username",
        read_only=True,
        allow_null=True,
    )
    academic_degree_name = serializers.CharField(
        source="academic_degree.name_ru",
        read_only=True,
        allow_null=True,
    )
    academic_title_name = serializers.CharField(
        source="academic_title.name_ru",
        read_only=True,
        allow_null=True,
    )
    employments = StaffEmploymentShortSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = StaffMember
        fields = (
            "id",
            "user",
            "username",
            "personnel_number",
            "last_name",
            "first_name",
            "middle_name",
            "full_name",
            "gender",
            "birth_date",
            "phone",
            "email",
            "academic_degree",
            "academic_degree_name",
            "academic_title",
            "academic_title_name",
            "has_academic_degree",
            "has_academic_title",
            "degree_awarded_date",
            "title_awarded_date",
            "is_active",
            "notes",
            "employments",
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
            "full_name",
            "has_academic_degree",
            "has_academic_title",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

    def validate_personnel_number(self, value):
        return value.strip().upper()

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        academic_degree = attrs.get(
            "academic_degree",
            getattr(instance, "academic_degree", None),
        )
        academic_title = attrs.get(
            "academic_title",
            getattr(instance, "academic_title", None),
        )
        degree_awarded_date = attrs.get(
            "degree_awarded_date",
            getattr(instance, "degree_awarded_date", None),
        )
        title_awarded_date = attrs.get(
            "title_awarded_date",
            getattr(instance, "title_awarded_date", None),
        )

        if degree_awarded_date and not academic_degree:
            raise serializers.ValidationError(
                {
                    "degree_awarded_date": (
                        "Нельзя указать дату без учёной степени."
                    )
                }
            )

        if title_awarded_date and not academic_title:
            raise serializers.ValidationError(
                {
                    "title_awarded_date": (
                        "Нельзя указать дату без учёного звания."
                    )
                }
            )

        return attrs

class StaffEmploymentSerializer(AuditFieldsSerializer):
    staff_member_name = serializers.CharField(
        source="staff_member.full_name",
        read_only=True,
    )
    department_name = serializers.CharField(
        source="department.name_ru",
        read_only=True,
    )
    faculty = serializers.IntegerField(
        source="department.faculty_id",
        read_only=True,
    )
    faculty_name = serializers.CharField(
        source="department.faculty.name_ru",
        read_only=True,
    )
    position_name = serializers.CharField(
        source="position.name_ru",
        read_only=True,
    )
    employment_type_name = serializers.CharField(
        source="get_employment_type_display",
        read_only=True,
    )

    class Meta:
        model = StaffEmployment
        fields = (
            "id",
            "staff_member",
            "staff_member_name",
            "department",
            "department_name",
            "faculty",
            "faculty_name",
            "position",
            "position_name",
            "employment_type",
            "employment_type_name",
            "rate",
            "start_date",
            "end_date",
            "is_primary",
            "is_active",
            "document_number",
            "document_date",
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
            "faculty",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        staff_member = attrs.get(
            "staff_member",
            getattr(instance, "staff_member", None),
        )
        department = attrs.get(
            "department",
            getattr(instance, "department", None),
        )
        position = attrs.get(
            "position",
            getattr(instance, "position", None),
        )
        start_date = attrs.get(
            "start_date",
            getattr(instance, "start_date", None),
        )
        end_date = attrs.get(
            "end_date",
            getattr(instance, "end_date", None),
        )
        is_primary = attrs.get(
            "is_primary",
            getattr(instance, "is_primary", False),
        )
        is_active = attrs.get(
            "is_active",
            getattr(instance, "is_active", True),
        )

        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "Дата окончания не может быть раньше "
                        "даты начала."
                    )
                }
            )

        if department:
            if department.is_archived or not department.is_active:
                raise serializers.ValidationError(
                    {
                        "department": (
                            "Выбранная кафедра недоступна."
                        )
                    }
                )

        if position:
            if position.is_archived or not position.is_active:
                raise serializers.ValidationError(
                    {
                        "position": (
                            "Выбранная должность недоступна."
                        )
                    }
                )

        if staff_member and is_primary and is_active:
            primary_queryset = StaffEmployment.objects.filter(
                staff_member=staff_member,
                is_primary=True,
                is_active=True,
            )

            if instance:
                primary_queryset = primary_queryset.exclude(
                    pk=instance.pk
                )

            if primary_queryset.exists():
                raise serializers.ValidationError(
                    {
                        "is_primary": (
                            "У сотрудника уже есть активное "
                            "основное назначение."
                        )
                    }
                )

        return attrs

class StaffEmploymentAcademicYearSerializer(
    AuditFieldsSerializer
):
    staff_member = serializers.IntegerField(
        source="staff_employment.staff_member_id",
        read_only=True,
    )
    staff_member_name = serializers.CharField(
        source="staff_employment.staff_member.full_name",
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
    academic_year_name = serializers.CharField(
        source="academic_year.name",
        read_only=True,
    )
    academic_degree_name = serializers.CharField(
        source="academic_degree.name_ru",
        read_only=True,
        allow_null=True,
    )
    academic_title_name = serializers.CharField(
        source="academic_title.name_ru",
        read_only=True,
        allow_null=True,
    )
    has_academic_degree = serializers.BooleanField(
        read_only=True,
    )
    has_academic_title = serializers.BooleanField(
        read_only=True,
    )
    recommended_annual_hours = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = StaffEmploymentAcademicYear
        fields = (
            "id",
            "staff_employment",
            "staff_member",
            "staff_member_name",
            "department",
            "department_name",
            "position_name",
            "academic_year",
            "academic_year_name",
            "rate",
            "academic_degree",
            "academic_degree_name",
            "academic_title",
            "academic_title_name",
            "has_academic_degree",
            "has_academic_title",
            "recommended_annual_hours",
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
            "staff_member",
            "department",
            "has_academic_degree",
            "has_academic_title",
            "recommended_annual_hours",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

    def get_recommended_annual_hours(self, obj):
        return obj.get_recommended_annual_hours()

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        employment = attrs.get(
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
        academic_degree = attrs.get(
            "academic_degree",
            getattr(
                instance,
                "academic_degree",
                None,
            ),
        )
        academic_title = attrs.get(
            "academic_title",
            getattr(
                instance,
                "academic_title",
                None,
            ),
        )

        if employment is not None:
            if employment.is_archived:
                raise serializers.ValidationError(
                    {
                        "staff_employment": (
                            "Назначение находится в архиве."
                        )
                    }
                )

            if not employment.is_active:
                raise serializers.ValidationError(
                    {
                        "staff_employment": (
                            "Назначение неактивно."
                        )
                    }
                )

        if (
            academic_degree is not None
            and (
                academic_degree.is_archived
                or not academic_degree.is_active
            )
        ):
            raise serializers.ValidationError(
                {
                    "academic_degree": (
                        "Выбранная учёная степень недоступна."
                    )
                }
            )

        if (
            academic_title is not None
            and (
                academic_title.is_archived
                or not academic_title.is_active
            )
        ):
            raise serializers.ValidationError(
                {
                    "academic_title": (
                        "Выбранное учёное звание недоступно."
                    )
                }
            )

        if employment and academic_year:
            duplicate_queryset = (
                StaffEmploymentAcademicYear.objects
                .filter(
                    staff_employment=employment,
                    academic_year=academic_year,
                )
            )

            if instance is not None:
                duplicate_queryset = (
                    duplicate_queryset.exclude(
                        pk=instance.pk
                    )
                )

            if duplicate_queryset.exists():
                raise serializers.ValidationError(
                    {
                        "academic_year": (
                            "Для этого назначения уже имеются "
                            "данные на выбранный учебный год."
                        )
                    }
                )

        return attrs

class WorkloadNormSerializer(AuditFieldsSerializer):
    academic_year_name = serializers.CharField(
        source="academic_year.name",
        read_only=True,
    )

    class Meta:
        model = WorkloadNorm
        fields = (
            "id",
            "academic_year",
            "academic_year_name",
            "rate",
            "has_academic_degree",
            "has_academic_title",
            "annual_hours",
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

class RecommendedWorkloadSerializer(serializers.Serializer):
    academic_year = serializers.IntegerField()
    employment = serializers.IntegerField()

class CreateAcademicYearStaffRecordsSerializer(
    serializers.Serializer
):
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.filter(
            is_active=True,
            is_archived=False,
        ),
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(
            is_active=True,
            is_archived=False,
        ),
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        academic_year = attrs["academic_year"]
        department = attrs.get("department")

        if academic_year.is_archived:
            raise serializers.ValidationError(
                {
                    "academic_year": (
                        "Учебный год находится в архиве."
                    )
                }
            )

        if not academic_year.is_active:
            raise serializers.ValidationError(
                {
                    "academic_year": (
                        "Учебный год неактивен."
                    )
                }
            )

        if department is not None:
            if department.is_archived:
                raise serializers.ValidationError(
                    {
                        "department": (
                            "Кафедра находится в архиве."
                        )
                    }
                )

            if not department.is_active:
                raise serializers.ValidationError(
                    {
                        "department": (
                            "Кафедра неактивна."
                        )
                    }
                )

        return attrs

class AcademicYearStaffRecordsResultSerializer(
    serializers.Serializer
):
    academic_year = serializers.IntegerField()
    academic_year_name = serializers.CharField()

    department = serializers.IntegerField(
        allow_null=True,
    )
    department_name = serializers.CharField(
        allow_null=True,
    )

    total_employments = serializers.IntegerField()
    created = serializers.IntegerField()
    restored = serializers.IntegerField()
    skipped = serializers.IntegerField()
    missing = serializers.IntegerField()

class MissingAcademicYearStaffRecordsSerializer(
    serializers.Serializer
):
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.filter(
            is_archived=False,
        ),
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(
            is_archived=False,
        ),
        required=False,
        allow_null=True,
    )