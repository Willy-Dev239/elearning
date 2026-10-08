from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Course, Lesson


class LessonInline(TabularInline):
    model = Lesson
    extra = 1
    fields = ("title", "kind", "file", "order")


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ("title", "classroom", "teacher", "created")
    list_filter = ("classroom", "teacher")
    search_fields = ("title", "description")
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
    list_display = ("title", "course", "kind", "order")
    list_filter = ("kind", "course")
    search_fields = ("title",)
