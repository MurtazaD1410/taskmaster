from rest_framework import serializers
from .models import Project
from users.serializers import UserSerializer


class ProjectSerializer(serializers.ModelSerializer):
    # By default, a read-only field will just return the author's ID.
    # This is a common and good approach.
    author = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "author",
            "created_at",
        ]
