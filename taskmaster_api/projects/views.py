from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Project, ProjectMembership
from .serializers import ProjectMemberSerializer, ProjectSerializer
from .permissions import IsMember, IsProjectOwner
from typing import cast
from users.models import CustomUser
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema


# Create your views here.
class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    A user can only see and edit their own project.
    """

    serializer_class = ProjectSerializer

    permission_classes = [permissions.IsAuthenticated, IsMember]

    def get_queryset(self):  # type: ignore
        if not self.request.user.is_authenticated:
            return Project.objects.none()  # Return an empty queryset

        # Step 2: Cast the authenticated user to your specific model.
        # This resolves the first error.
        user = cast(CustomUser, self.request.user)

        # Now this line is considered type-safe.
        return user.projects.all()

    def perform_create(self, serializer):
        """Ensure the author is the currently logged-in user."""
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        """
        Dynamically assign permissions based on the action.
        - Any member can view.
        - Only the owner can edit or delete.
        - Any authenticated user can create.
        """
        if self.action in ["retrieve", "list"]:
            # For viewing, you must be a member.
            permission_classes = [permissions.IsAuthenticated, IsMember]
        elif self.action in ["update", "partial_update", "destroy"]:
            # For editing/deleting, you must be the owner.
            permission_classes = [permissions.IsAuthenticated, IsProjectOwner]
        else:  # For 'create'
            # Any authenticated user can create a new project.
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]


class ProjectMemberRemoveView(APIView):
    """
    API view to remove a member from a project.
    """

    @extend_schema(responses={204: None})
    def delete(self, request, project_pk, user_pk):
        project = get_object_or_404(Project, pk=project_pk)
        user = get_object_or_404(CustomUser, pk=user_pk)

        if request.user != project.owner:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if user == project.owner:
            return Response(
                {"detail": "You cannot remove the owner from the project."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            membership = ProjectMembership.objects.get(project=project, user=user)
        except ProjectMembership.DoesNotExist:
            return Response(
                {"detail": "User is not a member of this project."},
                status=status.HTTP_404_NOT_FOUND,
            )

        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectMemberLeave(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMember]

    @extend_schema(responses={204: None})
    def delete(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk)

        if request.user == project.owner:
            return Response(
                {"detail": "You cannot leave the project as the owner."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            membership = ProjectMembership.objects.get(
                project=project, user=request.user
            )
        except:
            return Response(
                {"detail": "You are not a member of this project."},
                status=status.HTTP_404_NOT_FOUND,
            )

        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectMembersList(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMember]
    serializer_class = ProjectMemberSerializer

    def get(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk)

        try:
            ProjectMembership.objects.get(project=project, user=request.user)
        except:
            return Response(
                {"detail": "You are not a member of this project."},
                status=status.HTTP_404_NOT_FOUND,
            )
        memberships = ProjectMembership.objects.filter(project=project).select_related(
            "user"
        )
        serializer = self.get_serializer(memberships, many=True)
        return Response(serializer.data)
