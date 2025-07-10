from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.manager import Manager  # Import the Manager type

# We use a string 'Project' as a "forward reference" to avoid circular imports.
# If we tried to `from projects.models import Project`, it would likely crash.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from projects.models import Project


def avatar_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/avatars/user_<id>/<filename>
    return f"avatars/user_{instance.id}/{filename}"


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, help_text="A short biography of the user.")
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        null=True,
        blank=True,
        help_text="User's profile picture.",
    )
    projects: Manager["Project"]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
