from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class HealthCheckApiTests(APITestCase):
    def test_health_check_available_without_auth(
        self,
    ):
        response = self.client.get(
            reverse("common:health-check")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data,
            {
                "status": "ok",
                "service": (
                    "Управление учебным процессом"
                ),
                "api_version": "v1",
            },
        )

    def test_health_check_does_not_require_token(
        self,
    ):
        response = self.client.get(
            reverse("common:health-check"),
            HTTP_AUTHORIZATION=(
                "Bearer invalid-token"
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )