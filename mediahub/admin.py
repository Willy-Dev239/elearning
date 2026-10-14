from django.contrib import admin

from .models import CourseMaterial, MaterialProgress


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "kind", "file_size", "is_free_preview")
    list_filter = ("kind", "is_free_preview")


admin.site.register(MaterialProgress)
