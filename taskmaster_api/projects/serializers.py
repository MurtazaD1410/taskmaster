from rest_framework import serializers
from .models import Project
from users.serializers import UserSerializer


class ProjectSerializer(serializers.ModelSerializer):
    # By default, a read-only field will just return the author's ID.
    # This is a common and good approach.
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "owner",
            "members",
            "task_count",
            "created_at",
        ]

    def get_task_count(self, obj: Project) -> int:
        return obj.tasks.count()


class ProjectBasicSerializer(serializers.ModelSerializer):

    owner = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ["id", "title", "owner", "description"]
