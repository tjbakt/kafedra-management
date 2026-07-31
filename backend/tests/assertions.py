from rest_framework import status


class ApiResponseAssertionsMixin:
    """
    Общие проверки контрактов API.
    """

    def assert_error_response(
        self,
        response,
        *,
        status_code,
        code=None,
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

        self.assertIn(
            "error",
            response.data,
        )

        error = response.data["error"]

        self.assertIn(
            "code",
            error,
        )
        self.assertIn(
            "message",
            error,
        )
        self.assertIn(
            "fields",
            error,
        )
        self.assertIn(
            "details",
            error,
        )

        if code is not None:
            self.assertEqual(
                error["code"],
                code,
            )

        return error

    def assert_validation_error(
        self,
        response,
        *,
        field=None,
    ):
        error = self.assert_error_response(
            response,
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            code="validation_error",
        )

        if field is not None:
            self.assertIsNotNone(
                error["fields"]
            )
            self.assertIn(
                field,
                error["fields"],
            )

        return error

    def assert_authentication_required(
        self,
        response,
    ):
        return self.assert_error_response(
            response,
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            code="authentication_required",
        )

    def assert_permission_denied(
        self,
        response,
    ):
        return self.assert_error_response(
            response,
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            code="permission_denied",
        )

    def assert_not_found(
        self,
        response,
    ):
        return self.assert_error_response(
            response,
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            code="not_found",
        )

    def assert_paginated_response(
        self,
        response,
    ):
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        expected_fields = {
            "count",
            "page",
            "page_size",
            "total_pages",
            "next",
            "previous",
            "results",
        }

        self.assertEqual(
            set(response.data),
            expected_fields,
        )

        self.assertIsInstance(
            response.data["results"],
            list,
        )

        return response.data