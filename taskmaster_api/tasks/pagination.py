from rest_framework.pagination import PageNumberPagination


class TaskPagination(PageNumberPagination):
    """
    Custom pagination class specifically for Tasks.
    """

    page_size = 6  # How many tasks to show per page.

    # This is an optional but highly recommended setting.
    # It allows the client (your Vue frontend) to specify a page size
    # by adding `?page_size=50` to the URL.
    page_size_query_param = "page_size"

    # This is a security/performance measure. It sets the maximum number of items
    # the client is allowed to request in a single page.
    max_page_size = 100
