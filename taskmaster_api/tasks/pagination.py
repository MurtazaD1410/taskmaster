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

    def paginate_queryset(self, queryset, request, view=None):
        """
        Override the base method to check for a 'paginate' query parameter.
        """
        # Check if the query param `paginate=false` is present.
        # We check for the string 'false' to be explicit.
        if request.query_params.get("paginate", "true").lower() == "false":
            # If paginate=false, return None to disable pagination for this request.
            return None

        # Otherwise, perform the default pagination behavior.
        return super().paginate_queryset(queryset, request, view)
