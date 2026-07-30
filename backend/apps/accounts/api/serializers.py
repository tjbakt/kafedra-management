from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)

from django.contrib.auth.password_validation import (
    validate_password,
)
from drf_spectacular.utils import (
    extend_schema_field,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        read_only=True,
    )
    groups = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "middle_name",
            "full_name",
            "phone",
            "avatar",
            "interface_language",
            "must_change_password",
            "is_active",
            "is_staff",
            "groups",
            "permissions",
            "last_login",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "username",
            "must_change_password",
            "is_active",
            "is_staff",
            "groups",
            "permissions",
            "last_login",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(
        serializers.ListField(
            child=serializers.CharField(),
        )
    )
    def get_groups(self, obj,) -> list[str]:
        return list(obj.groups.order_by("name").values_list(
                "name",
                flat=True,
            )
        )

    @extend_schema_field(
        serializers.ListField(
            child=serializers.CharField(),
        )
    )
    def get_permissions(self,obj,) -> list[str]:
        return sorted(
            obj.get_all_permissions()
        )


class CustomTokenObtainPairSerializer(
    TokenObtainPairSerializer
):
    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = UserSerializer(
            self.user,
            context=self.context,
        ).data

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["username"] = user.username
        token["full_name"] = user.full_name
        token["language"] = user.interface_language

        token["groups"] = list(
            user.groups.order_by("name").values_list(
                "name",
                flat=True,
            )
        )

        return token


class TokenResponseSerializer(
    serializers.Serializer
):
    """
    Ответ успешной JWT-аутентификации.
    """

    refresh = serializers.CharField(
        read_only=True,
    )
    access = serializers.CharField(
        read_only=True,
    )
    user = UserSerializer(
        read_only=True,
    )


class TokenRefreshRequestSerializer(
    serializers.Serializer
):
    refresh = serializers.CharField()


class TokenRefreshResponseSerializer(
    serializers.Serializer
):
    access = serializers.CharField(
        read_only=True,
    )
    refresh = serializers.CharField(
        read_only=True,
        required=False,
    )

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        required=True,
        allow_blank=False,
    )


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )
    new_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        # min_length=8,
    )
    new_password_confirmation = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate_current_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                "Текущий пароль указан неверно."
            )

        return value

    def validate_new_password(self, value):
        user = self.context["request"].user
        validate_password(value, user=user)
        return value

    def validate(self, attrs):
        if (
            attrs["new_password"]
            != attrs["new_password_confirmation"]
        ):
            raise serializers.ValidationError(
                {
                    "new_password_confirmation": (
                        "Пароли не совпадают."
                    )
                }
            )

        return attrs

class TokenVerifyRequestSerializer(
    serializers.Serializer
):
    token = serializers.CharField(
        help_text=(
            "JWT-токен, который требуется проверить."
        ),
    )


class TokenVerifyResponseSerializer(
    serializers.Serializer
):
    """
    Успешная проверка токена возвращает пустой JSON-объект.
    """