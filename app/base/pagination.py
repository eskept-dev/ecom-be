from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'per_page'

    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            'total_page': self.page.paginator.num_pages,
            'per_page': self.page.paginator.per_page,
            'page': self.page.number,
            'results': data
        })
