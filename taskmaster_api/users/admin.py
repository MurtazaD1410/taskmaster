from django.contrib import admin


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "bio", "avatar")


# Register your models here.
from .models import CustomUser


admin.site.register(CustomUser, UserAdmin)
