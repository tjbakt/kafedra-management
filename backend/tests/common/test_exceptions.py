from django.core.exceptions import (
    PermissionDenied as DjangoPermissionDenied,
)
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.http import Http404
from django.test import SimpleTestCase
from rest_framework.exceptions import (
    AuthenticationFailed,
    ErrorDetail,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    ParseError,
    PermissionDenied,
    ValidationError,
)

from apps.common.api.exceptions import (
    convert_django_exception,
    custom_exception_handler,
    django_validation_to_drf,
    error_detail_code,
    error_detail_message,
    first_plain_value,
    normalize_error_detail,
)


class ErrorNormalizationTests(
    SimpleTestCase
):
    def test_normalize_error_detail(self):
        value = {
            "name": [
                ErrorDetail(
                    "Обязательное поле.",
                    code="required",
                )
            ]
        }

        result = normalize_error_detail(
            value
        )

        self.assertEqual(
            result,
            {
                "name": [
                    {
                        "message": (
                            "Обязательное поле."
                        ),
                        "code": "required",
                    }
                ]
            },
        )

    def test_error_detail_message(self):
        value = {
            "name": [
                ErrorDetail(
                    "Некорректно.",
                    code="invalid",
                )
            ]
        }

        self.assertEqual(
            error_detail_message(value),
            "Некорректно.",
        )

    def test_error_detail_code(self):
        value = {
            "name": [
                ErrorDetail(
                    "Некорректно.",
                    code="invalid",
                )
            ]
        }

        self.assertEqual(
            error_detail_code(value),
            "invalid",
        )

    def test_first_plain_value(self):
        value = {
            "detail": [
                ErrorDetail(
                    "Первая ошибка.",
                    code="invalid",
                )
            ]
        }

        self.assertEqual(
            first_plain_value(value),
            "Первая ошибка.",
        )


class DjangoExceptionConversionTests(
    SimpleTestCase
):
    def test_django_validation_to_drf(
        self,
    ):
        result = django_validation_to_drf(
            DjangoValidationError(
                {
                    "name": [
                        DjangoValidationError(
                            "Ошибка.",
                            code="custom",
                        )
                    ]
                }
            )
        )

        self.assertIsInstance(
            result,
            ValidationError,
        )
        self.assertEqual(
            result.detail["name"][0].code,
            "custom",
        )

    def test_http404_is_converted(self):
        result = convert_django_exception(
            Http404()
        )

        self.assertIsInstance(
            result,
            NotFound,
        )

    def test_django_permission_is_converted(
        self,
    ):
        result = convert_django_exception(
            DjangoPermissionDenied()
        )

        self.assertIsInstance(
            result,
            PermissionDenied,
        )

    def test_unknown_exception_is_unchanged(
        self,
    ):
        error = RuntimeError("failure")

        self.assertIs(
            convert_django_exception(error),
            error,
        )


class CustomExceptionHandlerTests(
    SimpleTestCase
):
    context = {
        "view": None,
        "request": None,
    }

    def handle(self, exc):
        return custom_exception_handler(
            exc,
            self.context,
        )

    def assert_envelope(
        self,
        response,
        *,
        status_code,
        code,
    ):
        self.assertEqual(
            response.status_code,
            status_code,
        )
        self.assertFalse(
            response.data["success"]
        )
        self.assertEqual(
            response.data["status_code"],
            status_code,
        )
        self.assertEqual(
            response.data["error"]["code"],
            code,
        )
        self.assertIn(
            "message",
            response.data["error"],
        )
        self.assertIn(
            "fields",
            response.data["error"],
        )
        self.assertIn(
            "details",
            response.data["error"],
        )

    def test_validation_error(self):
        response = self.handle(
            ValidationError(
                {
                    "name": [
                        ErrorDetail(
                            "Обязательное поле.",
                            code="required",
                        )
                    ]
                }
            )
        )

        self.assert_envelope(
            response,
            status_code=400,
            code="validation_error",
        )

        self.assertEqual(
            response.data["error"]["fields"][
                "name"
            ][0],
            {
                "message": (
                    "Обязательное поле."
                ),
                "code": "required",
            },
        )

    def test_not_authenticated(self):
        response = self.handle(
            NotAuthenticated()
        )

        self.assert_envelope(
            response,
            status_code=401,
            code="authentication_required",
        )

    def test_authentication_failed(self):
        response = self.handle(
            AuthenticationFailed()
        )

        self.assert_envelope(
            response,
            status_code=401,
            code="authentication_failed",
        )

    def test_permission_denied(self):
        response = self.handle(
            PermissionDenied()
        )

        self.assert_envelope(
            response,
            status_code=403,
            code="permission_denied",
        )

    def test_not_found(self):
        response = self.handle(
            NotFound()
        )

        self.assert_envelope(
            response,
            status_code=404,
            code="not_found",
        )

    def test_method_not_allowed(self):
        response = self.handle(
            MethodNotAllowed("POST")
        )

        self.assert_envelope(
            response,
            status_code=405,
            code="method_not_allowed",
        )

    def test_parse_error(self):
        response = self.handle(
            ParseError()
        )

        self.assert_envelope(
            response,
            status_code=400,
            code="parse_error",
        )

    def test_django_validation_error(self):
        response = self.handle(
            DjangoValidationError(
                {
                    "title": [
                        "Некорректный заголовок."
                    ]
                }
            )
        )

        self.assert_envelope(
            response,
            status_code=400,
            code="validation_error",
        )
        self.assertIn(
            "title",
            response.data["error"]["fields"],
        )

    def test_unhandled_exception_returns_none(
        self,
    ):
        response = self.handle(
            RuntimeError("unexpected")
        )

        self.assertIsNone(response)