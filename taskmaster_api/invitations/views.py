from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.exceptions import PermissionDenied
from projects.models import Project
from .serializers import (
    InvitationSerializer,
    ActionInvitationSerializer,
    PendingInvitationSerializer,
)
from .models import Invitation
from django.db.models.query import QuerySet
from rest_framework.response import Response
from typing import cast
from users.models import CustomUser


# Create your views here.
class InvitationCreateView(generics.CreateAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        project = Project.objects.get(pk=self.kwargs["project_pk"])

        if self.request.user != project.owner:
            raise PermissionDenied("You are not the owner of this project.")

        serializer.save(project=project, invited_by=self.request.user)


class AcceptInvitationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActionInvitationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]

        try:
            invitation = Invitation.objects.get(
                token=token, status=Invitation.Status.PENDING
            )
        except Invitation.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired invitation token."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.email != invitation.email:
            return Response(
                {"detail": "Invalid invitation email"}, status=status.HTTP_403_FORBIDDEN
            )

        invitation.project.members.add(request.user)
        invitation.status = Invitation.Status.ACCEPTED
        invitation.save()

        return Response(
            {"detail": "Invitation accepted successfully."}, status=status.HTTP_200_OK
        )


class DeclineInvitationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActionInvitationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]

        try:
            invitation = Invitation.objects.get(
                token=token, status=Invitation.Status.PENDING
            )
        except Invitation.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired invitation token."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.email != invitation.email:
            return Response(
                {"detail": "Invalid invitation email"}, status=status.HTTP_403_FORBIDDEN
            )

        invitation.status = Invitation.Status.DECLINED
        invitation.save()

        return Response({"detail": "Invitation declined."}, status=status.HTTP_200_OK)


class PendingInvitationListView(generics.ListAPIView):
    """
    API endpoint to list all pending invitations for the currently authenticated user.
    """

    serializer_class = PendingInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[Invitation]:  # type: ignore
        """
        This view should return a list of all the pending invitations
        for the currently authenticated user.
        """

        user = cast(CustomUser, self.request.user)

        return (
            Invitation.objects.filter(
                email__iexact=user.email,
            )
            .exclude(status=Invitation.Status.ACCEPTED)
            .select_related("project", "invited_by")
        )
