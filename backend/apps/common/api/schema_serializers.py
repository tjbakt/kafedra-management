from rest_framework import serializers


class ApiErrorItemSerializer(
    serializers.Serializer
):
    """
    Одна нормализованная ошибка поля.
    """

    message = serializers.CharField()
    code = serializers.CharField()


class ApiErrorSerializer(
    serializers.Serializer
):
    """
    Содержимое поля error единого API-контракта.
    """

    code = serializers.CharField()
    message = serializers.CharField()

    fields = serializers.DictField(
        required=False,
        allow_null=True,
        help_text=(
            "Ошибки отдельных полей. "
            "Значения обычно являются списками "
            "объектов с message и code."
        ),
    )

    details = serializers.DictField(
        required=False,
        allow_null=True,
        help_text=(
            "Дополнительные сведения "
            "о бизнес-ошибке."
        ),
    )


class ApiErrorResponseSerializer(
    serializers.Serializer
):
    """
    Единый ошибочный ответ API.
    """

    success = serializers.BooleanField(
        default=False,
    )
    status_code = serializers.IntegerField()
    error = ApiErrorSerializer()


class DetailResponseSerializer(
    serializers.Serializer
):
    """
    Простой успешный ответ с сообщением.
    """

    detail = serializers.CharField()


class IdListSerializer(serializers.Serializer):
    """
    Список идентификаторов объектов.
    """

    ids = serializers.ListField(
        child=serializers.IntegerField(
            min_value=1,
        ),
        allow_empty=False,
    )


class ArchiveResponseSerializer(
    serializers.Serializer
):
    """
    Результат архивирования объекта.
    """

    detail = serializers.CharField()


class RestoreResponseSerializer(
    serializers.Serializer
):
    """
    Базовое представление восстановления.

    Поле data зависит от сериализатора конкретного
    ViewSet, поэтому описано как JSON-объект.
    """

    detail = serializers.CharField()
    data = serializers.DictField()


class PaginationMetaSerializer(
    serializers.Serializer
):
    """
    Документирует метаданные стандартной пагинации.
    """

    count = serializers.IntegerField(
        min_value=0,
    )
    page = serializers.IntegerField(
        min_value=1,
    )
    page_size = serializers.IntegerField(
        min_value=1,
    )
    total_pages = serializers.IntegerField(
        min_value=0,
    )
    next = serializers.URLField(
        allow_null=True,
    )
    previous = serializers.URLField(
        allow_null=True,
    )
    results = serializers.ListField()