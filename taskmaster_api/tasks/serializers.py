from rest_framework import serializers
from .models import Task
from users.serializers import UserSerializer
from projects.models import Project
from projects.serializers import ProjectSerializer


class TaskSerializer(serializers.ModelSerializer):
    # By default, a read-only field will just return the author's ID.
    # This is a common and good approach.
    author = UserSerializer(read_only=True)
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        write_only=True,
        required=False,  # Make it optional if tasks can exist without a project
        allow_null=True,  # Also allow null to be sent
    )
    project_details = ProjectSerializer(source="project", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "project",
            "project_details",
            "author",
            "created_at",
        ]

    def validate_project(self, project):
        """
        Check if project is owned by the current user
        """
        if project and project.author != self.context["request"].user:
            raise serializers.ValidationError(
                "You can only assign tasks to your own projects."
            )
        return project
