from apps.common.api.api_exceptions import (
    BusinessRuleViolation,
    ConflictError,
)


def raise_business_error(
    *,
    code,
    message,
    details=None,
    fields=None,
):
    """
    Выбрасывает HTTP 400 для нарушения
    бизнес-правила.
    """

    raise BusinessRuleViolation(
        detail=message,
        code=code,
        details=details,
        fields=fields,
    )


def raise_conflict_error(
    *,
    code,
    message,
    details=None,
    fields=None,
):
    """
    Выбрасывает HTTP 409 для конфликта
    текущего состояния ресурса.
    """

    raise ConflictError(
        detail=message,
        code=code,
        details=details,
        fields=fields,
    )