from rest_framework import serializers

from apps.access_control.models import (
    SystemRole,
    UserRoleAssignment,
)
from apps.common.api.serializers import AuditFieldsSerializer


class SystemRoleSerializer(AuditFieldsSerializer):
    class Meta:
        model = SystemRole
        fields = (
            "id",
            "code",
            "name_ru",
            "name_uz",
            "description",
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


class UserRoleAssignmentSerializer(
    AuditFieldsSerializer
):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    user_full_name = serializers.SerializerMethodField()
    role_code = serializers.CharField(
        source="role.code",
        read_only=True,
    )
    role_name = serializers.CharField(
        source="role.name_ru",
        read_only=True,
    )
    scope_type_name = serializers.CharField(
        source="get_scope_type_display",
        read_only=True,
    )
    university_name = serializers.CharField(
        source="university.name_ru",
        read_only=True,
        allow_null=True,
    )
    faculty_name = serializers.CharField(
        source="faculty.name_ru",
        read_only=True,
        allow_null=True,
    )
    department_name = serializers.CharField(
        source="department.name_ru",
        read_only=True,
        allow_null=True,
    )
    staff_member_name = serializers.CharField(
        source="staff_member.full_name",
        read_only=True,
        allow_null=True,
    )
    is_current = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = UserRoleAssignment
        fields = (
            "id",
            "user",
            "username",
            "user_full_name",
            "role",
            "role_code",
            "role_name",
            "scope_type",
            "scope_type_name",
            "university",
            "university_name",
            "faculty",
            "faculty_name",
            "department",
            "department_name",
            "staff_member",
            "staff_member_name",
            "valid_from",
            "valid_until",
            "is_active",
            "is_current",
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

    def get_user_full_name(self, obj):
        if hasattr(obj.user, "get_full_name"):
            return (
                obj.user.get_full_name()
                or obj.user.username
            )

        return str(obj.user)

    def validate(self, attrs):
        instance = self.instance

        user = attrs.get(
            "user",
            getattr(instance, "user", None),
        )

        role = attrs.get(
            "role",
            getattr(instance, "role", None),
        )
        scope_type = attrs.get(
            "scope_type",
            getattr(instance, "scope_type", None),
        )
        university = attrs.get(
            "university",
            getattr(instance, "university", None),
        )
        faculty = attrs.get(
            "faculty",
            getattr(instance, "faculty", None),
        )
        department = attrs.get(
            "department",
            getattr(instance, "department", None),
        )
        staff_member = attrs.get(
            "staff_member",
            getattr(instance, "staff_member", None),
        )
        valid_from = attrs.get(
            "valid_from",
            getattr(instance, "valid_from", None),
        )
        valid_until = attrs.get(
            "valid_until",
            getattr(instance, "valid_until", None),
        )

        if (
                user
                and staff_member
                and staff_member.user_id
                and staff_member.user_id != user.id
        ):
            raise serializers.ValidationError(
                {
                    "staff_member": (
                        "Карточка сотрудника связана "
                        "с другим пользователем."
                    )
                }
            )
        if (
                role
                and role.code == SystemRole.Code.TEACHER
                and staff_member
                and not staff_member.user_id
        ):
            raise serializers.ValidationError(
                {
                    "staff_member": (
                        "Карточка преподавателя не связана "
                        "с учётной записью пользователя."
                    )
                }
            )

        required_fields = {
            UserRoleAssignment.ScopeType.GLOBAL: (),
            UserRoleAssignment.ScopeType.UNIVERSITY: (
                "university",
            ),
            UserRoleAssignment.ScopeType.FACULTY: (
                "faculty",
            ),
            UserRoleAssignment.ScopeType.DEPARTMENT: (
                "department",
            ),
            UserRoleAssignment.ScopeType.SELF: (
                "staff_member",
            ),
        }

        values = {
            "university": university,
            "faculty": faculty,
            "department": department,
            "staff_member": staff_member,
        }

        for field_name in required_fields.get(
            scope_type,
            (),
        ):
            if not values[field_name]:
                raise serializers.ValidationError(
                    {
                        field_name: (
                            "Поле обязательно для выбранной "
                            "области действия."
                        )
                    }
                )

        if faculty and university:
            if faculty.university_id != university.id:
                raise serializers.ValidationError(
                    {
                        "faculty": (
                            "Факультет не относится "
                            "к выбранному университету."
                        )
                    }
                )

        if department and faculty:
            if department.faculty_id != faculty.id:
                raise serializers.ValidationError(
                    {
                        "department": (
                            "Кафедра не относится "
                            "к выбранному факультету."
                        )
                    }
                )

        if (
            valid_from
            and valid_until
            and valid_until < valid_from
        ):
            raise serializers.ValidationError(
                {
                    "valid_until": (
                        "Дата окончания не может быть раньше "
                        "даты начала."
                    )
                }
            )

        if (
            role
            and role.code == SystemRole.Code.TEACHER
            and scope_type
            != UserRoleAssignment.ScopeType.SELF
        ):
            raise serializers.ValidationError(
                {
                    "scope_type": (
                        "Для преподавателя должна использоваться "
                        "персональная область."
                    )
                }
            )

        if (
            role
            and role.code
            == SystemRole.Code.DEPARTMENT_HEAD
            and scope_type
            != UserRoleAssignment.ScopeType.DEPARTMENT
        ):
            raise serializers.ValidationError(
                {
                    "scope_type": (
                        "Для заведующего кафедрой необходимо "
                        "выбрать кафедральную область."
                    )
                }
            )

        return attrs