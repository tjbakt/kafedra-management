from rest_framework.exceptions import ErrorDetail
from rest_framework.views import exception_handler


def normalize_errors(detail):
    """
    Преобразует ошибки DRF в обычные структуры Python.
    """

    if isinstance(detail, dict):
        return {
            key: normalize_errors(value)
            for key, value in detail.items()
        }

    if isinstance(detail, list):
        return [
            normalize_errors(value)
            for value in detail
        ]

    if isinstance(detail, ErrorDetail):
        return {
            "message": str(detail),
            "code": detail.code,
        }

    return detail


def custom_exception_handler(exc, context):
    """
    Формирует единый ответ для обработанных исключений DRF.
    """

    response = exception_handler(exc, context)

    if response is None:
        return None

    original_data = response.data
    error_code = getattr(exc, "default_code", "error")

    if isinstance(original_data, dict):
        detail = original_data.get("detail")

        if detail is not None:
            message = str(detail)
            errors = None
        else:
            message = "Ошибка проверки данных."
            errors = normalize_errors(original_data)
    else:
        message = "Ошибка выполнения запроса."
        errors = normalize_errors(original_data)

    response.data = {
        "success": False,
        "status_code": response.status_code,
        "error": {
            "code": error_code,
            "message": message,
            "fields": errors,
        },
    }

    return response