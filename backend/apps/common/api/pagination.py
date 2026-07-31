from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPageNumberPagination(
    PageNumberPagination
):
    """
    Стандартная пагинация проекта.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(
        self,
        data,
    ):
        return Response(
            {
                "count": self.page.paginator.count,
                "page": self.page.number,
                "page_size": self.get_page_size(
                    self.request
                ),
                "total_pages": (
                    self.page.paginator.num_pages
                ),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

    def get_paginated_response_schema(
        self,
        schema,
    ):
        """
        Точная OpenAPI-схема фактического ответа.
        """

        return {
            "type": "object",
            "required": [
                "count",
                "page",
                "page_size",
                "total_pages",
                "results",
            ],
            "properties": {
                "count": {
                    "type": "integer",
                    "example": 125,
                    "description": (
                        "Общее количество записей."
                    ),
                },
                "page": {
                    "type": "integer",
                    "example": 2,
                    "description": (
                        "Номер текущей страницы."
                    ),
                },
                "page_size": {
                    "type": "integer",
                    "example": 20,
                    "minimum": 1,
                    "maximum": self.max_page_size,
                    "description": (
                        "Количество записей "
                        "на текущей странице."
                    ),
                },
                "total_pages": {
                    "type": "integer",
                    "example": 7,
                    "description": (
                        "Общее количество страниц."
                    ),
                },
                "next": {
                    "type": "string",
                    "format": "uri",
                    "nullable": True,
                    "example": (
                        "https://example.test/api/v1/"
                        "workload/distributions/"
                        "?page=3&page_size=20"
                    ),
                    "description": (
                        "Ссылка на следующую страницу."
                    ),
                },
                "previous": {
                    "type": "string",
                    "format": "uri",
                    "nullable": True,
                    "example": (
                        "https://example.test/api/v1/"
                        "workload/distributions/"
                        "?page=1&page_size=20"
                    ),
                    "description": (
                        "Ссылка на предыдущую страницу."
                    ),
                },
                "results": schema,
            },
        }