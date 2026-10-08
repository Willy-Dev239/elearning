from django.conf import settings
from django.db import models


class Course(models.Model):
    classroom = models.ForeignKey("schools.Classroom", on_delete=models.CASCADE, related_name="courses", verbose_name="Classe")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses", verbose_name="Enseignant")
    title = models.CharField("Titre", max_length=200)
    description = models.TextField("Description", blank=True)
    created = models.DateTimeField("Créé le", auto_now_add=True)

    class Meta:
        verbose_name = "cours"
        verbose_name_plural = "cours"

    def __str__(self):
        return self.title


class Lesson(models.Model):
    class Kind(models.TextChoices):
        VIDEO = "VIDEO", "Vidéo"
        DOCUMENT = "DOCUMENT", "Document"

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Cours")
    title = models.CharField("Titre", max_length=200)
    kind = models.CharField("Type", max_length=10, choices=Kind.choices, default=Kind.VIDEO)
    file = models.FileField("Fichier", upload_to="lessons/%Y/%m/")
    order = models.PositiveIntegerField("Ordre", default=0)
    created = models.DateTimeField("Ajoutée le", auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "leçon"
        verbose_name_plural = "leçons"

    def __str__(self):
        return self.title
