from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 10  # Default number of items per page
    page_size_query_param = "page_size"  # Query parameter to control the page size
    max_page_size = 1000  # Maximum allowed page size
