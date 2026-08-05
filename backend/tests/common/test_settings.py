from django.conf import settings
from django.test import SimpleTestCase


class RestFrameworkSettingsTests(
    SimpleTestCase
):
    def test_custom_exception_handler_enabled(
        self,
    ):
        self.assertEqual(
            settings.REST_FRAMEWORK[
                "EXCEPTION_HANDLER"
            ],
            (
                "apps.common.api.exceptions."
                "custom_exception_handler"
            ),
        )

    def test_standard_pagination_enabled(
        self,
    ):
        self.assertEqual(
            settings.REST_FRAMEWORK[
                "DEFAULT_PAGINATION_CLASS"
            ],
            (
                "apps.common.api.pagination."
                "StandardPageNumberPagination"
            ),
        )