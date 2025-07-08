from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project
import uuid

User = get_user_model()


# Create your models here.
class Invitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "P", "Pending"
        ACCEPTED = "A", "Accepted"
        DECLINED = "D", "Declined"

    email = models.EmailField()
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="invitations"
    )
    invited_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_invitations"
    )

    # A unique token for the user to accept the invitation
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(
        max_length=1, choices=Status.choices, default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user can only be invited to a project once while the invite is pending.
        unique_together = ("email", "project", "status")

    def __str__(self):
        return f"Invitation for {self.email} to {self.project.title}"
