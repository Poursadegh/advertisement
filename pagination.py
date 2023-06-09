from rest_framework import pagination
from rest_framework import status
from rest_framework.exceptions import NotFound as NotFoundError
from rest_framework.pagination import PageNumberPagination  # Any other type works as well
from rest_framework.response import Response
from collections import OrderedDict


class Pagination(pagination.PageNumberPagination):


    page_size = 10
    page_size_query_param = 'page_size'


class AdvertisementPagination(PageNumberPagination):

    page_size = 10

    def generate_response(self, query_set, serializer_obj, request):
        try:
            page_data = self.paginate_queryset(query_set, request)
        except NotFoundError:
            return Response({"error": "No results found for the requested page"}, status=status.HTTP_400_BAD_REQUEST)

        serialized_page = serializer_obj(page_data, many=True, context={'request': request})
        return self.get_paginated_response(serialized_page.data)


class CustomPaginator(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        """
        PageNumberPagination response override
        """
        return Response(OrderedDict([
            ('total_count', self.page.paginator.count),  # total # of objects that will be paginated
            ('page_size', self.get_page_size(self.request)),  # total # on current page
            ('page_number', int(self.request.query_params.get(self.page_query_param, 1))),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
