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
            "priority",
            "order",
            "deadline",
            "author",
            "created_at",
        ]

    def validate_project(self, project):
        """
        Check that the user is a member of the project they are
        assigning the task to.
        """
        # Get the current user from the context that DRF provides.
        user = self.context["request"].user

        # The new, correct check: is the user in the project's members list?
        # The .exists() check is an efficient way to do this.
        if not project.members.filter(id=user.id).exists():
            # If they are not a member, raise the validation error with a new message.
            raise serializers.ValidationError(
                "You can only assign tasks to projects you are a member of."
            )

        # If the check passes, always return the project value. This is required.
        return project


class TaskOrderUpdateSerializer(serializers.Serializer):
    """
    Serializer for the batch task order/status update endpoint.
    Validates the incoming data structure.
    """

    # Use a ChoiceField to ensure the status is valid.
    status = serializers.ChoiceField(choices=Task.Status.choices, required=True)

    # Use a ListField with a child to ensure we get a list of integers.
    ordered_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=True,  # Don't allow empty lists
    )
