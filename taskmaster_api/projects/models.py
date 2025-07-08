from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.manager import Manager  # Import the Manager type


User = get_user_model()

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tasks.models import Task


# Create your models here.
class Project(models.Model):

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_projects"
    )
    members = models.ManyToManyField(
        User, through="ProjectMembership", blank=True, related_name="projects"
    )
    tasks: Manager["Task"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # This check ensures this logic runs only when the project is first created.
        is_new = self._state.adding
        super().save(*args, **kwargs)  # Save the project first
        if is_new:
            ProjectMembership.objects.create(
                project=self, user=self.owner, role=ProjectMembership.Role.OWNER
            )


class ProjectMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        MEMBER = "member", "Member"

    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "user")

    def __str__(self):
        return f"{self.user.username} - {self.project.title} ({self.role})"
