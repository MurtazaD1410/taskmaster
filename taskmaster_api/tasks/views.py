from rest_framework import viewsets, permissions, status, generics
from .models import Task
from django.db.models import Q
from .serializers import TaskOrderUpdateSerializer, TaskSerializer
from django.db.models.query import QuerySet
from .permissions import IsProjectMemberForTask
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.response import Response
from .pagination import TaskPagination
from rest_framework.request import Request
from django.db import transaction


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

    filterset_fields = ["status", "project", "author"]
    pagination_class = TaskPagination
    request: Request

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

        tasks_in_my_projects = Q(project__members=user)
        my_personal_tasks = Q(author=user, project__isnull=True)

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


class TaskOrderUpdateView(generics.GenericAPIView):
    """
    An API endpoint to handle batch updates of task order and status.
    Expects a POST request with a 'status' and a list of ordered_ids.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskOrderUpdateSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        # Inside this block, Pylance now understands that
        # `serializer.validated_data` is guaranteed to be a dictionary.

        # The errors on these lines will disappear.
        status_update = serializer.validated_data["status"]
        ordered_ids = serializer.validated_data["ordered_ids"] or []

        # The rest of your logic remains the same.
        for index, task_id in enumerate(ordered_ids):
            Task.objects.filter(id=task_id).update(order=index, status=status_update)

        return Response(
            {"detail": "Task order updated successfully."},
            status=status.HTTP_200_OK,
        )
