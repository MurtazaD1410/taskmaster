from rest_framework import viewsets, permissions
from .models import Project
from .serializers import ProjectSerializer
from django.db.models.query import QuerySet
from .permissions import IsOwner


# Create your views here.
class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    A user can only see and edit their own project.
    """

    serializer_class = ProjectSerializer

    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self) -> QuerySet[Project]:  # type: ignore
        """
        This view should return a list of all the tasks
        for the currently authenticated user.
        """

        user = self.request.user
        return Project.objects.filter(author=user)

    def perform_create(self, serializer):
        """Ensure the author is the currently logged-in user."""
        serializer.save(author=self.request.user)
