from typing import Any

from drf_spectacular.utils import (
    extend_schema_field,
)
from rest_framework import serializers


class AuditFieldsSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для моделей с полями аудита.
    """

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    archived_by_name = serializers.SerializerMethodField()


    @extend_schema_field(
        serializers.CharField(
            allow_null=True,
        )
    )
    def get_created_by_name(
        self,
        obj: Any,
    ) -> str | None:
        if not obj.created_by:
            return None

        return (
            obj.created_by.full_name
            or obj.created_by.username
        )

    @extend_schema_field(
        serializers.CharField(
            allow_null=True,
        )
    )
    def get_updated_by_name(
        self,
        obj: Any,
    ) -> str | None:
        if not obj.updated_by:
            return None

        return (
            obj.updated_by.full_name
            or obj.updated_by.username
        )

    @extend_schema_field(
        serializers.CharField(
            allow_null=True,
        )
    )
    def get_archived_by_name(
        self,
        obj: Any,
    ) -> str | None:
        if not obj.archived_by:
            return None

        return (
            obj.archived_by.full_name
            or obj.archived_by.username
        )