from rest_framework import serializers


class WorkloadValidationIssueSerializer(
    serializers.Serializer
):
    """
    Одна проблема, обнаруженная при проверке
    нагрузки учебного года.
    """

    code = serializers.CharField()
    message = serializers.CharField()

    object_type = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    object_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    details = serializers.DictField(
        required=False,
        allow_null=True,
    )


class AcademicYearWorkloadValidationResponseSerializer(
    serializers.Serializer
):
    """
    Результат проверки нагрузки учебного года.

    Поля сделаны частично необязательными, чтобы
    схема не навязывала бизнес-сервису структуру,
    которой в конкретной проверке может не быть.
    """

    academic_year = serializers.IntegerField()
    academic_year_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    is_valid = serializers.BooleanField()

    errors_count = serializers.IntegerField(
        min_value=0,
        required=False,
    )
    warnings_count = serializers.IntegerField(
        min_value=0,
        required=False,
    )

    errors = WorkloadValidationIssueSerializer(
        many=True,
        required=False,
    )
    warnings = WorkloadValidationIssueSerializer(
        many=True,
        required=False,
    )

    summary = serializers.DictField(
        required=False,
        allow_null=True,
    )


class AcademicYearClosingReadinessResponseSerializer(
    serializers.Serializer
):
    """
    Результат проверки готовности учебного года
    к закрытию.
    """

    academic_year = serializers.IntegerField()
    academic_year_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    is_ready = serializers.BooleanField()

    blockers_count = serializers.IntegerField(
        min_value=0,
        required=False,
    )
    warnings_count = serializers.IntegerField(
        min_value=0,
        required=False,
    )

    blockers = WorkloadValidationIssueSerializer(
        many=True,
        required=False,
    )
    warnings = WorkloadValidationIssueSerializer(
        many=True,
        required=False,
    )

    summary = serializers.DictField(
        required=False,
        allow_null=True,
    )