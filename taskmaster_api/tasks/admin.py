from django.contrib import admin


# Register your models here.
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "project",
        "author",
        "created_at",
        "updated_at",
    )
    search_fields = ("title", "description")
    list_filter = ("created_at", "updated_at", "author")


# Register your models here.
from .models import Task


admin.site.register(Task, TaskAdmin)
