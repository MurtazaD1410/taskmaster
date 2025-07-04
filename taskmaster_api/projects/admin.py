from django.contrib import admin


# Register your models here.
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "updated_at")
    search_fields = ("title", "description")
    list_filter = ("created_at", "updated_at", "author")


# Register your models here.
from .models import Project


admin.site.register(Project, ProjectAdmin)
