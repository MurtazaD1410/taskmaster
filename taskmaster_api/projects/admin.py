from django.contrib import admin
from .models import Project, ProjectMembership


# Register your models here.
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "created_at", "updated_at")
    search_fields = ("title", "description")
    list_filter = ("created_at", "updated_at", "owner")


class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "role", "joined_at")


admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectMembership, ProjectMembershipAdmin)
