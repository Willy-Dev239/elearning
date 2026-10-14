from django.contrib import admin

from .models import AcademicYear, Course, Enrollment, Grade, TimetableSlot


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "teacher", "price", "is_published")
    search_fields = ("code", "title")
    list_filter = ("is_published", "academic_year")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "status", "enrolled_at")
    list_filter = ("status",)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "title", "score", "max_score", "coefficient")


admin.site.register(AcademicYear)
admin.site.register(TimetableSlot)
