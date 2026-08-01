from django.utils.translation import get_language
from rest_framework import serializers

from apps.common.api.serializers import AuditFieldsSerializer
from apps.organizations.models import (
    Department,
    Faculty,
    University,
)
from drf_spectacular.utils import (
    extend_schema_field,
)


class OrganizationSerializerMixin:

    def get_current_language(self, obj):
        request = self.context.get("request")

        if (
            request
            and request.user
            and request.user.is_authenticated
        ):
            return request.user.interface_language

        language = get_language() or "ru"
        return language[:2]

    @extend_schema_field(
        serializers.CharField()
    )
    def get_display_name(self, obj) -> str:
        language = self.get_current_language(obj)

        if language == "uz":
            return obj.name_uz or obj.name_ru

        return obj.name_ru or obj.name_uz

    @extend_schema_field(
        serializers.CharField()
    )
    def get_display_short_name(self, obj) -> str:
        language = self.get_current_language(obj)

        if language == "uz":
            return (
                obj.short_name_uz
                or obj.short_name_ru
                or obj.name_uz
            )

        return (
            obj.short_name_ru
            or obj.short_name_uz
            or obj.name_ru
        )

    def validate_code(self, value):
        return value.strip().upper()

    def validate_name_ru(self, value):
        return value.strip()

    def validate_name_uz(self, value):
        return value.strip()

    def validate_short_name_ru(self, value):
        return value.strip()

    def validate_short_name_uz(self, value):
        return value.strip()


class UniversitySerializer(
    OrganizationSerializerMixin,
    AuditFieldsSerializer,
):
    display_name = serializers.SerializerMethodField()
    display_short_name = serializers.SerializerMethodField()
    faculties_count = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = University
        fields = (
            "id",
            "code",
            "name_ru",
            "name_uz",
            "short_name_ru",
            "short_name_uz",
            "display_name",
            "display_short_name",
            "address_ru",
            "address_uz",
            "phone",
            "email",
            "website",
            "is_active",
            "sort_order",
            "faculties_count",
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
            "display_short_name",
            "faculties_count",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )


class FacultyShortSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Faculty
        fields = (
            "id",
            "code",
            "display_name",
        )
        read_only_fields = (
            "id",
            "code",
            "display_name",
        )

    @extend_schema_field(
        serializers.CharField()
    )
    def get_display_name(self, obj) -> str:
        request = self.context.get("request")

        language = (
            request.user.interface_language
            if request
            and request.user.is_authenticated
            else (get_language() or "ru")[:2]
        )

        if language == "uz":
            return obj.name_uz or obj.name_ru

        return obj.name_ru or obj.name_uz


class FacultySerializer(
    OrganizationSerializerMixin,
    AuditFieldsSerializer,
):
    display_name = serializers.SerializerMethodField()
    display_short_name = serializers.SerializerMethodField()
    university_name = serializers.CharField(
        source="university.name_ru",
        read_only=True,
    )
    departments_count = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Faculty
        fields = (
            "id",
            "university",
            "university_name",
            "faculty_type",
            "code",
            "name_ru",
            "name_uz",
            "short_name_ru",
            "short_name_uz",
            "display_name",
            "display_short_name",
            "dean_name",
            "phone",
            "email",
            "is_active",
            "sort_order",
            "departments_count",
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
            "display_short_name",
            "departments_count",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

    def validate_university(self, value):
        if value.is_archived:
            raise serializers.ValidationError(
                "Нельзя выбрать архивный университет."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "Нельзя выбрать неактивный университет."
            )

        return value


class DepartmentSerializer(
    OrganizationSerializerMixin,
    AuditFieldsSerializer,
):
    display_name = serializers.SerializerMethodField()
    display_short_name = serializers.SerializerMethodField()
    faculty_name = serializers.CharField(
        source="faculty.name_ru",
        read_only=True,
    )
    university = serializers.IntegerField(
        source="faculty.university_id",
        read_only=True,
    )
    university_name = serializers.CharField(
        source="faculty.university.name_ru",
        read_only=True,
    )

    class Meta:
        model = Department
        fields = (
            "id",
            "faculty",
            "faculty_name",
            "university",
            "university_name",
            "code",
            "name_ru",
            "name_uz",
            "short_name_ru",
            "short_name_uz",
            "display_name",
            "display_short_name",
            "head_name",
            "phone",
            "email",
            "room",
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
            "display_short_name",
            "university",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

    def validate_faculty(self, value):
        if value.is_archived:
            raise serializers.ValidationError(
                "Нельзя выбрать архивный факультет."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "Нельзя выбрать неактивный факультет."
            )

        if value.university.is_archived:
            raise serializers.ValidationError(
                "Университет выбранного факультета архивирован."
            )

        return value