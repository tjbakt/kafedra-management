from rest_framework import status
from rest_framework.exceptions import APIException


class BusinessRuleViolation(APIException):
    """
    Нарушение бизнес-правила.

    Используется, когда запрос синтаксически корректен,
    но операция запрещена текущим состоянием данных.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Операция нарушает бизнес-правило."
    default_code = "business_rule_violation"

    def __init__(
        self,
        detail=None,
        *,
        code=None,
        details=None,
        fields=None,
    ):
        super().__init__(
            detail=detail,
            code=code,
        )

        self.error_code = (
            code or self.default_code
        )
        self.error_details = details
        self.error_fields = fields


class ConflictError(APIException):
    """
    Конфликт текущего состояния ресурса.

    Примеры:
    - повторное выполнение перехода состояния;
    - конфликт версии;
    - ресурс уже существует;
    - операция несовместима с текущим статусом.
    """

    status_code = status.HTTP_409_CONFLICT
    default_detail = (
        "Операция конфликтует с текущим "
        "состоянием ресурса."
    )
    default_code = "conflict"

    def __init__(
        self,
        detail=None,
        *,
        code=None,
        details=None,
        fields=None,
    ):
        super().__init__(
            detail=detail,
            code=code,
        )

        self.error_code = (
            code or self.default_code
        )
        self.error_details = details
        self.error_fields = fields


class ResourceStateConflict(ConflictError):
    """
    Конфликт состояния конкретного ресурса.
    """

    default_detail = (
        "Операция недоступна в текущем "
        "состоянии ресурса."
    )
    default_code = "resource_state_conflict"


class DuplicateResourceError(ConflictError):
    """
    Попытка создать логически дублирующий ресурс.
    """

    default_detail = "Такая запись уже существует."
    default_code = "duplicate_resource"