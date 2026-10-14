from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "is_active")
    list_filter = ("role", "is_active")
    fieldsets = UserAdmin.fieldsets + (("École", {"fields": ("role", "phone")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("École", {"fields": ("email", "role", "phone")}),)
