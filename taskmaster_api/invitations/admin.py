from django.contrib import admin


# Register your models here.
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "project", "token", "status")
    search_fields = ("email", "project")


# Register your models here.
from .models import Invitation


admin.site.register(Invitation, InvitationAdmin)
