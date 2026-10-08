from django.conf import settings
from django.db import models


class School(models.Model):
    name = models.CharField(max_length=150, unique=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Classroom(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="classrooms")
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("school", "name")

    def __str__(self):
        return f"{self.school} — {self.name}"


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="enrollments", limit_choices_to={"role": "STUDENT"})
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="enrollments")
    academic_year = models.CharField(max_length=9, default="2026-2027")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "classroom", "academic_year")

    def __str__(self):
        return f"{self.student} → {self.classroom} ({self.academic_year})"
