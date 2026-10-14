import os
import uuid

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


def material_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"courses/{instance.course_id}/{uuid.uuid4().hex}{ext}"


class CourseMaterial(TimeStampedModel):
    class Kind(models.TextChoices):
        VIDEO = "video", "Vidéo"
        DOCUMENT = "document", "Document"
        AUDIO = "audio", "Audio"

    course = models.ForeignKey("academic.Course", on_delete=models.CASCADE, related_name="materials")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    kind = models.CharField(max_length=10, choices=Kind.choices)
    file = models.FileField(upload_to=material_upload_path)
    file_size = models.BigIntegerField(default=0)
    content_type = models.CharField(max_length=100, blank=True)
    is_free_preview = models.BooleanField(
        default=False, help_text="Visible même sans inscription ni paiement."
    )
    position = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+"
    )

    class Meta:
        ordering = ["course", "position", "id"]

    def __str__(self):
        return f"{self.course.code} — {self.title}"


class MaterialProgress(TimeStampedModel):
    """Suivi de lecture d'un support par un étudiant."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="material_progress"
    )
    material = models.ForeignKey(CourseMaterial, on_delete=models.CASCADE, related_name="progress")
    completed = models.BooleanField(default=False)
    last_position_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "material"], name="unique_student_material")
        ]
