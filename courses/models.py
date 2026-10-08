from django.conf import settings
from django.db import models


class Course(models.Model):
    classroom = models.ForeignKey("schools.Classroom", on_delete=models.CASCADE, related_name="courses")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    class Kind(models.TextChoices):
        VIDEO = "VIDEO", "Vidéo"
        DOCUMENT = "DOCUMENT", "Document"

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.VIDEO)
    file = models.FileField(upload_to="lessons/%Y/%m/")
    order = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title
