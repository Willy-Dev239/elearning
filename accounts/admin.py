from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from config.admin_base import ModelAdmin
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import User

admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    search_fields = ("name",)
    filter_horizontal = ("permissions",)


@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ("username", "full_name", "role_label", "email", "phone", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("username", "first_name", "last_name", "email", "phone")
    fieldsets = UserAdmin.fieldsets + (("Profil", {"fields": ("role", "phone")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Profil", {"fields": ("first_name", "last_name", "email", "role", "phone")}),)

    @display(description="Nom complet")
    def full_name(self, obj):
        return obj.get_full_name() or "—"

    @display(description="Rôle", label={"Étudiant": "info", "Enseignant": "success", "Back office": "warning"})
    def role_label(self, obj):
        return obj.get_role_display()
