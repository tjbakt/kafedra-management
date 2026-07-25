from rest_framework import serializers


class AuditFieldsSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для моделей с аудитом.
    """

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    archived_by_name = serializers.SerializerMethodField()

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return None

        return obj.created_by.full_name or obj.created_by.username

    def get_updated_by_name(self, obj):
        if not obj.updated_by:
            return None

        return obj.updated_by.full_name or obj.updated_by.username

    def get_archived_by_name(self, obj):
        if not obj.archived_by:
            return None

        return obj.archived_by.full_name or obj.archived_by.username