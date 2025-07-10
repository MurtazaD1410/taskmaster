from django.db import models
from django.contrib.auth import get_user_model

from projects.models import Project


# Create your models here.
class Task(models.Model):
    User = get_user_model()

    class Priority(models.TextChoices):
        LOW = "L", "Low"
        MEDIUM = "M", "Medium"
        HIGH = "H", "High"

    class Status(models.TextChoices):
        TODO = "TODO", "To Do"
        BACKLOG = "BACKLOG", "Backlog"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        DONE = "DONE", "Done"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
    )
    priority = models.CharField(
        max_length=1,
        choices=Priority.choices,
        null=True,
        blank=True,
        help_text="Optional priority level of the task.",
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    order = models.PositiveIntegerField(default=0, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks", null=True, blank=True
    )
    deadline = models.DateTimeField(
        blank=True, null=True, help_text="The date and time the task is due."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        # ordering = ["-created_at"]
        ordering = ["order"]
