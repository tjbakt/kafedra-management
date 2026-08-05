from django.test import TestCase
from rest_framework.test import (
    APIRequestFactory,
)
from rest_framework.request import Request

from apps.common.api.pagination import (
    StandardPageNumberPagination,
)


class StandardPaginationTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def paginate(
        self,
        items,
        *,
        query_string="",
    ):
        raw_request = self.factory.get(
            f"/test/{query_string}"
        )
        request = Request(raw_request)

        paginator = (
            StandardPageNumberPagination()
        )

        page = paginator.paginate_queryset(
            items,
            request,
        )

        response = (
            paginator.get_paginated_response(
                page
            )
        )

        return page, response

    def test_default_page_size(self):
        page, response = self.paginate(
            list(range(25))
        )

        self.assertEqual(len(page), 20)
        self.assertEqual(
            response.data["count"],
            25,
        )
        self.assertEqual(
            response.data["page"],
            1,
        )
        self.assertEqual(
            response.data["page_size"],
            20,
        )
        self.assertEqual(
            response.data["total_pages"],
            2,
        )
        self.assertEqual(
            response.data["results"],
            list(range(20)),
        )
        self.assertIsNotNone(
            response.data["next"]
        )
        self.assertIsNone(
            response.data["previous"]
        )

    def test_custom_page_size(self):
        page, response = self.paginate(
            list(range(12)),
            query_string="?page_size=5",
        )

        self.assertEqual(len(page), 5)
        self.assertEqual(
            response.data["page_size"],
            5,
        )
        self.assertEqual(
            response.data["total_pages"],
            3,
        )

    def test_second_page(self):
        page, response = self.paginate(
            list(range(12)),
            query_string=(
                "?page=2&page_size=5"
            ),
        )

        self.assertEqual(
            list(page),
            [5, 6, 7, 8, 9],
        )
        self.assertEqual(
            response.data["page"],
            2,
        )
        self.assertIsNotNone(
            response.data["previous"]
        )

    def test_page_size_is_limited_to_100(
        self,
    ):
        page, response = self.paginate(
            list(range(150)),
            query_string="?page_size=500",
        )

        self.assertEqual(len(page), 100)
        self.assertEqual(
            response.data["page_size"],
            100,
        )

    def test_response_contract(self):
        _, response = self.paginate(
            list(range(3))
        )

        self.assertEqual(
            set(response.data),
            {
                "count",
                "page",
                "page_size",
                "total_pages",
                "next",
                "previous",
                "results",
            },
        )