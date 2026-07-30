from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
)

from apps.common.api.schema_serializers import (
    ApiErrorResponseSerializer,
    DetailResponseSerializer,
)


VALIDATION_ERROR_EXAMPLE = OpenApiExample(
    name="Ошибка валидации",
    value={
        "success": False,
        "status_code": 400,
        "error": {
            "code": "validation_error",
            "message": (
                "Ошибка проверки данных."
            ),
            "fields": {
                "name": [
                    {
                        "message": (
                            "Это поле обязательно."
                        ),
                        "code": "required",
                    }
                ]
            },
            "details": None,
        },
    },
    response_only=True,
    status_codes=["400"],
)


AUTHENTICATION_ERROR_EXAMPLE = OpenApiExample(
    name="Требуется аутентификация",
    value={
        "success": False,
        "status_code": 401,
        "error": {
            "code": (
                "authentication_required"
            ),
            "message": (
                "Учетные данные не были "
                "предоставлены."
            ),
            "fields": None,
            "details": None,
        },
    },
    response_only=True,
    status_codes=["401"],
)


PERMISSION_ERROR_EXAMPLE = OpenApiExample(
    name="Недостаточно прав",
    value={
        "success": False,
        "status_code": 403,
        "error": {
            "code": "permission_denied",
            "message": "Доступ запрещён.",
            "fields": None,
            "details": None,
        },
    },
    response_only=True,
    status_codes=["403"],
)


NOT_FOUND_ERROR_EXAMPLE = OpenApiExample(
    name="Объект не найден",
    value={
        "success": False,
        "status_code": 404,
        "error": {
            "code": "not_found",
            "message": (
                "Запрашиваемый ресурс "
                "не найден."
            ),
            "fields": None,
            "details": None,
        },
    },
    response_only=True,
    status_codes=["404"],
)


CONFLICT_ERROR_EXAMPLE = OpenApiExample(
    name="Конфликт состояния",
    value={
        "success": False,
        "status_code": 409,
        "error": {
            "code": "resource_state_conflict",
            "message": (
                "Операция недоступна "
                "в текущем состоянии ресурса."
            ),
            "fields": None,
            "details": {
                "status": "approved",
            },
        },
    },
    response_only=True,
    status_codes=["409"],
)


BAD_REQUEST_RESPONSE = OpenApiResponse(
    response=ApiErrorResponseSerializer,
    description="Ошибка проверки данных.",
    examples=[
        VALIDATION_ERROR_EXAMPLE,
    ],
)


UNAUTHORIZED_RESPONSE = OpenApiResponse(
    response=ApiErrorResponseSerializer,
    description="Требуется аутентификация.",
    examples=[
        AUTHENTICATION_ERROR_EXAMPLE,
    ],
)


FORBIDDEN_RESPONSE = OpenApiResponse(
    response=ApiErrorResponseSerializer,
    description="Недостаточно прав.",
    examples=[
        PERMISSION_ERROR_EXAMPLE,
    ],
)


NOT_FOUND_RESPONSE = OpenApiResponse(
    response=ApiErrorResponseSerializer,
    description="Ресурс не найден.",
    examples=[
        NOT_FOUND_ERROR_EXAMPLE,
    ],
)


CONFLICT_RESPONSE = OpenApiResponse(
    response=ApiErrorResponseSerializer,
    description=(
        "Конфликт текущего состояния ресурса."
    ),
    examples=[
        CONFLICT_ERROR_EXAMPLE,
    ],
)


NO_CONTENT_RESPONSE = OpenApiResponse(
    response=None,
    description="Операция выполнена успешно.",
)


DETAIL_RESPONSE = OpenApiResponse(
    response=DetailResponseSerializer,
    description="Операция выполнена успешно.",
)


COMMON_AUTH_ERROR_RESPONSES = {
    401: UNAUTHORIZED_RESPONSE,
    403: FORBIDDEN_RESPONSE,
}


COMMON_OBJECT_ERROR_RESPONSES = {
    400: BAD_REQUEST_RESPONSE,
    401: UNAUTHORIZED_RESPONSE,
    403: FORBIDDEN_RESPONSE,
    404: NOT_FOUND_RESPONSE,
}


COMMON_MUTATION_ERROR_RESPONSES = {
    400: BAD_REQUEST_RESPONSE,
    401: UNAUTHORIZED_RESPONSE,
    403: FORBIDDEN_RESPONSE,
    404: NOT_FOUND_RESPONSE,
    409: CONFLICT_RESPONSE,
}