from collections.abc import Mapping, Sequence

from django.core.exceptions import (
    PermissionDenied as DjangoPermissionDenied,
)
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    ErrorDetail,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    ParseError,
    PermissionDenied,
    Throttled,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.common.api.api_exceptions import (
    BusinessRuleViolation,
    ConflictError,
)


DEFAULT_MESSAGES = {
    status.HTTP_400_BAD_REQUEST: (
        "Ошибка проверки данных."
    ),
    status.HTTP_401_UNAUTHORIZED: (
        "Требуется аутентификация."
    ),
    status.HTTP_403_FORBIDDEN: (
        "Доступ запрещён."
    ),
    status.HTTP_404_NOT_FOUND: (
        "Запрашиваемый ресурс не найден."
    ),
    status.HTTP_405_METHOD_NOT_ALLOWED: (
        "HTTP-метод не поддерживается."
    ),
    status.HTTP_409_CONFLICT: (
        "Конфликт состояния ресурса."
    ),
    status.HTTP_429_TOO_MANY_REQUESTS: (
        "Превышено допустимое количество запросов."
    ),
    status.HTTP_500_INTERNAL_SERVER_ERROR: (
        "Внутренняя ошибка сервера."
    ),
}


DEFAULT_CODES = {
    status.HTTP_400_BAD_REQUEST: "bad_request",
    status.HTTP_401_UNAUTHORIZED: (
        "authentication_required"
    ),
    status.HTTP_403_FORBIDDEN: (
        "permission_denied"
    ),
    status.HTTP_404_NOT_FOUND: "not_found",
    status.HTTP_405_METHOD_NOT_ALLOWED: (
        "method_not_allowed"
    ),
    status.HTTP_409_CONFLICT: "conflict",
    status.HTTP_429_TOO_MANY_REQUESTS: (
        "throttled"
    ),
    status.HTTP_500_INTERNAL_SERVER_ERROR: (
        "server_error"
    ),
}


RESERVED_DETAIL_KEYS = {
    "code",
    "detail",
    "message",
    "non_field_errors",
}


def normalize_error_detail(value):
    """
    Преобразует ErrorDetail и вложенные структуры
    DRF в JSON-совместимые структуры.

    Каждая конечная ошибка получает форму:

    {
        "message": "...",
        "code": "..."
    }
    """

    if isinstance(value, ErrorDetail):
        return {
            "message": str(value),
            "code": value.code,
        }

    if isinstance(value, Mapping):
        return {
            str(key): normalize_error_detail(
                nested_value
            )
            for key, nested_value in value.items()
        }

    if (
        isinstance(value, Sequence)
        and not isinstance(
            value,
            (
                str,
                bytes,
                bytearray,
            ),
        )
    ):
        return [
            normalize_error_detail(item)
            for item in value
        ]

    return value


def error_detail_message(value):
    """
    Получает человекочитаемое сообщение из
    ErrorDetail, строки или списка ошибок.
    """

    if isinstance(value, ErrorDetail):
        return str(value)

    if isinstance(value, str):
        return value

    if isinstance(value, Mapping):
        for nested_value in value.values():
            message = error_detail_message(
                nested_value
            )
            if message:
                return message

        return None

    if (
        isinstance(value, Sequence)
        and not isinstance(
            value,
            (
                str,
                bytes,
                bytearray,
            ),
        )
    ):
        for item in value:
            message = error_detail_message(item)
            if message:
                return message

    return None


def error_detail_code(value):
    """
    Получает первый конкретный код из структуры
    ErrorDetail.
    """

    if isinstance(value, ErrorDetail):
        return value.code

    if isinstance(value, Mapping):
        for nested_value in value.values():
            code = error_detail_code(
                nested_value
            )
            if code:
                return code

        return None

    if (
        isinstance(value, Sequence)
        and not isinstance(
            value,
            (
                str,
                bytes,
                bytearray,
            ),
        )
    ):
        for item in value:
            code = error_detail_code(item)
            if code:
                return code

    return None


def first_plain_value(value):
    """
    Извлекает первое простое значение.

    Используется для специальных полей code,
    detail и message, которые после преобразования
    Django ValidationError могут быть списками.
    """

    if isinstance(value, ErrorDetail):
        return str(value)

    if isinstance(value, Mapping):
        if "message" in value:
            return first_plain_value(
                value["message"]
            )

        for nested_value in value.values():
            result = first_plain_value(
                nested_value
            )
            if result is not None:
                return result

        return None

    if (
        isinstance(value, Sequence)
        and not isinstance(
            value,
            (
                str,
                bytes,
                bytearray,
            ),
        )
    ):
        for item in value:
            result = first_plain_value(item)
            if result is not None:
                return result

        return None

    return value


def django_validation_to_drf(
    exc,
):
    """
    Преобразует django.core ValidationError
    в DRF ValidationError.

    Сохраняет message_dict и коды отдельных ошибок.
    """

    if hasattr(exc, "error_dict"):
        detail = {}

        for field_name, errors in (
            exc.error_dict.items()
        ):
            detail[field_name] = [
                ErrorDetail(
                    error.message,
                    code=(
                        error.code
                        or "invalid"
                    ),
                )
                for error in errors
            ]

        return ValidationError(detail)

    errors = getattr(
        exc,
        "error_list",
        (),
    )

    detail = [
        ErrorDetail(
            error.message,
            code=(
                error.code
                or "invalid"
            ),
        )
        for error in errors
    ]

    return ValidationError(
        detail or exc.messages
    )


def convert_django_exception(exc):
    """
    Преобразует стандартные Django-исключения
    в аналоги DRF.
    """

    if isinstance(
        exc,
        DjangoValidationError,
    ):
        return django_validation_to_drf(exc)

    if isinstance(exc, Http404):
        return NotFound()

    if isinstance(
        exc,
        DjangoPermissionDenied,
    ):
        return PermissionDenied()

    return exc


def resolve_status_code(
    exc,
    response,
):
    if isinstance(exc, ConflictError):
        return status.HTTP_409_CONFLICT

    return response.status_code


def resolve_error_code(
    exc,
    *,
    response_data,
    status_code,
):
    """
    Определяет стабильный верхнеуровневый код.

    Для DRF ValidationError ключ `code` может быть
    обычным полем сериализатора, поэтому сначала
    проверяется тип исключения.
    """

    explicit_code = getattr(
        exc,
        "error_code",
        None,
    )
    if explicit_code:
        return str(explicit_code)

    if isinstance(
        exc,
        ValidationError,
    ):
        return "validation_error"

    if isinstance(
        response_data,
        Mapping,
    ):
        supplied_code = response_data.get(
            "code"
        )

        # Верхнеуровневый служебный code должен быть
        # простым скалярным значением. Список ошибок
        # означает поле сериализатора с именем code.
        if isinstance(
            supplied_code,
            (
                str,
                ErrorDetail,
            ),
        ):
            return str(supplied_code)

    if isinstance(exc, ParseError):
        return "parse_error"

    if isinstance(exc, NotAuthenticated):
        return "authentication_required"

    if isinstance(exc, AuthenticationFailed):
        return "authentication_failed"

    if isinstance(exc, PermissionDenied):
        return "permission_denied"

    if isinstance(exc, NotFound):
        return "not_found"

    if isinstance(exc, MethodNotAllowed):
        return "method_not_allowed"

    if isinstance(exc, Throttled):
        return "throttled"

    return str(
        getattr(
            exc,
            "default_code",
            None,
        )
        or DEFAULT_CODES.get(
            status_code,
            "error",
        )
    )

def resolve_message(
    exc,
    *,
    response_data,
    status_code,
):
    """
    Получает основное человекочитаемое сообщение.
    """

    if isinstance(response_data, Mapping):
        for key in (
            "message",
            "detail",
        ):
            if key in response_data:
                message = first_plain_value(
                    response_data[key]
                )

                if message:
                    return str(message)

    direct_message = error_detail_message(
        response_data
    )
    if direct_message:
        return direct_message

    default_detail = getattr(
        exc,
        "default_detail",
        None,
    )
    if default_detail:
        return str(default_detail)

    return DEFAULT_MESSAGES.get(
        status_code,
        "Ошибка выполнения запроса.",
    )


def resolve_fields(
    exc,
    *,
    response_data,
):
    """
    Возвращает ошибки конкретных полей.

    """

    explicit_fields = getattr(
        exc,
        "error_fields",
        None,
    )

    if explicit_fields is not None:
        return normalize_error_detail(
            explicit_fields
        )

    if not isinstance(response_data, Mapping,):
        return None

    if (
            "code" in response_data
            or "detail" in response_data
            or "message" in response_data
    ):
        return None

    fields = {
        str(key): value
        for key, value in response_data.items()
        if key not in RESERVED_DETAIL_KEYS
    }

    non_field_errors = response_data.get(
        "non_field_errors"
    )
    if non_field_errors is not None:
        fields["non_field_errors"] = (
            non_field_errors
        )

    if not fields:
        return None

    return normalize_error_detail(fields)


def resolve_details(
    exc,
    *,
    response_data,
):
    """
    Возвращает дополнительные сведения,
    не являющиеся ошибками serializer-полей.
    """

    explicit_details = getattr(
        exc,
        "error_details",
        None,
    )

    if explicit_details is not None:
        return normalize_error_detail(
            explicit_details
        )

    if not isinstance(
        response_data,
        Mapping,
    ):
        return None

    if not any(
        key in response_data
        for key in (
            "code",
            "detail",
            "message",
        )
    ):
        return None

    details = {
        str(key): normalize_error_detail(value)
        for key, value in response_data.items()
        if key not in RESERVED_DETAIL_KEYS
    }

    return details or None


def build_error_response(
    *,
    exc,
    response,
):
    """
    Формирует окончательный контракт ошибки.
    """

    response_data = response.data
    status_code = resolve_status_code(
        exc,
        response,
    )

    error_code = resolve_error_code(
        exc,
        response_data=response_data,
        status_code=status_code,
    )

    message = resolve_message(
        exc,
        response_data=response_data,
        status_code=status_code,
    )

    fields = resolve_fields(
        exc,
        response_data=response_data,
    )

    details = resolve_details(
        exc,
        response_data=response_data,
    )

    response.status_code = status_code

    response.data = {
        "success": False,
        "status_code": status_code,
        "error": {
            "code": error_code,
            "message": message,
            "fields": fields,
            "details": details,
        },
    }

    return response


def custom_exception_handler(exc, context):
    """
    Глобальный обработчик ошибок REST API.

    Необработанные исключения оставляются Django:
    в production они будут преобразованы в HTTP 500,
    а в development сохранят traceback.
    """

    converted_exc = convert_django_exception(
        exc
    )

    response = exception_handler(
        converted_exc,
        context,
    )

    if response is None:
        if isinstance(
            converted_exc,
            (
                BusinessRuleViolation,
                ConflictError,
                APIException,
            ),
        ):
            response = Response(
                converted_exc.detail,
                status=(
                    converted_exc.status_code
                ),
            )
        else:
            return None

    return build_error_response(
        exc=converted_exc,
        response=response,
    )