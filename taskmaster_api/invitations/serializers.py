from rest_framework import serializers
from projects.serializers import ProjectBasicSerializer, ProjectSerializer
from users.serializers import UserSerializer
from .models import Invitation


class InvitationSerializer(serializers.ModelSerializer):
    # By default, a read-only field will just return the author's ID.
    # This is a common and good approach.
    project = ProjectSerializer(read_only=True)
    invited_by = UserSerializer(read_only=True)

    class Meta:
        model = Invitation
        fields = ["id", "email", "project", "invited_by", "status", "token"]
        read_only_fields = ["status", "token"]


class ActionInvitationSerializer(serializers.Serializer):
    token = serializers.UUIDField()


class PendingInvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for listing pending invitations.
    Includes nested details about the project and the person who invited the user.
    """

    project = ProjectBasicSerializer()
    invited_by = UserSerializer()

    class Meta:
        model = Invitation
        fields = [
            "id",
            "project",
            "invited_by",
            "status",
            "token",
            "created_at",
        ]
