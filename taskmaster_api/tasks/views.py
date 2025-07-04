from rest_framework import viewsets, permissions
from .models import Task
from .serializers import TaskSerializer
from django.db.models.query import QuerySet
from .permissions import IsOwner
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


# Create your views here.
class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tasks to be viewed or edited.
    A user can only see and edit their own tasks.
    Supports filtering by status, e.g., /api/tasks/?status=TODO
    """

    serializer_class = TaskSerializer
    # allow only logged in users
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    filterset_fields = ["status", "project"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="status",
                description="Filter by task status (e.g., TODO, IN_PROGRESS)",
                required=False,
                type=str,
                enum=[choice[0] for choice in Task.Status.choices],
            ),
            # --- ADD THIS NEW PARAMETER FOR THE PROJECT FILTER ---
            OpenApiParameter(
                name="project",
                description="Filter tasks by Project ID",
                required=False,
                type=OpenApiTypes.INT,  # Use INT since it's an ID
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Returns a list of tasks for the authenticated user.
        Can be filtered by the 'status' query parameter.
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Task]:  # type: ignore
        """
        This view should return a list of all the tasks
        for the currently authenticated user.
        """
        user = self.request.user
        return Task.objects.filter(author=user)

    def perform_create(self, serializer):
        """Ensure the author is the currently logged-in user."""
        serializer.save(author=self.request.user)
