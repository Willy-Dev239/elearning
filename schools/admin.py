from django.contrib import admin
from config.admin_base import ModelAdmin

from .models import Classroom, Enrollment, School


@admin.register(School)
class SchoolAdmin(ModelAdmin):
    list_display = ("name", "address")
    search_fields = ("name",)


@admin.register(Classroom)
class ClassroomAdmin(ModelAdmin):
    list_display = ("name", "school")
    list_filter = ("school",)
    search_fields = ("name",)


@admin.register(Enrollment)
class EnrollmentAdmin(ModelAdmin):
    list_display = ("student", "classroom", "academic_year", "created")
    list_filter = ("classroom", "academic_year")
    search_fields = ("student__username", "student__first_name", "student__last_name")
    autocomplete_fields = ("student",)
