from rest_framework import viewsets, permissions, status
from .models import Task
from django.db.models import Q
from .serializers import TaskSerializer
from django.db.models.query import QuerySet
from .permissions import IsProjectMemberForTask
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.response import Response
from .pagination import TaskPagination


from typing import cast
from users.models import CustomUser


# Create your views here.
class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tasks to be viewed or edited.
    A user can only see and edit their own tasks.
    Supports filtering by status, e.g., /api/tasks/?status=TODO
    """

    serializer_class = TaskSerializer
    # allow only logged in users
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberForTask]

    filterset_fields = ["status", "project"]
    pagination_class = TaskPagination

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
        Returns a list of tasks that meet one of two conditions:
        1. The task is in a project where the user is a member.
        2. The task has no project assigned AND was created by the user.
        """
        # First, handle the unauthenticated case for type safety
        if not self.request.user.is_authenticated:
            return Task.objects.none()

        user = cast(CustomUser, self.request.user)

        # Condition 1: Tasks in projects the user is a member of.
        # This is your existing logic.
        tasks_in_my_projects = Q(project__members=user)

        # Condition 2: "Personal" tasks created by the user that have no project.
        # `project__isnull=True` checks for tasks where the project foreign key is NULL.
        my_personal_tasks = Q(author=user, project__isnull=True)

        # Combine the two conditions with an OR operator (|).
        # The .distinct() is important to prevent duplicate tasks from appearing
        # if a user is the author of a task in a project they are also a member of.
        return Task.objects.filter(tasks_in_my_projects | my_personal_tasks).distinct()

    def perform_create(self, serializer):
        """Ensure the author is the currently logged-in user."""
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Override the create method to add a permission check.
        A user can only create a task in a project they are a member of.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = serializer.validated_data.get("project")

        if project:
            # If we are inside this block, we know 'project' is a real Project object,
            # so it's safe to access its .members attribute.
            if not project.members.filter(id=request.user.id).exists():
                return Response(
                    {
                        "detail": "You are not a member of this project and cannot create tasks in it."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
