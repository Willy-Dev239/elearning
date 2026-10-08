from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "role", "email")
    list_filter = ("role",)
    fieldsets = UserAdmin.fieldsets + (("Profil", {"fields": ("role", "phone")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Profil", {"fields": ("role", "phone")}),)
