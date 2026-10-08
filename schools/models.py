from django.conf import settings
from django.db import models


class School(models.Model):
    name = models.CharField("Nom", max_length=150, unique=True)
    address = models.CharField("Adresse", max_length=255, blank=True)

    class Meta:
        verbose_name = "école"
        verbose_name_plural = "écoles"

    def __str__(self):
        return self.name


class Classroom(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="classrooms", verbose_name="École")
    name = models.CharField("Nom de la classe", max_length=100)

    class Meta:
        unique_together = ("school", "name")
        verbose_name = "classe"
        verbose_name_plural = "classes"

    def __str__(self):
        return f"{self.school} — {self.name}"


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments",
                                limit_choices_to={"role": "STUDENT"}, verbose_name="Étudiant")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="enrollments", verbose_name="Classe")
    academic_year = models.CharField("Année académique", max_length=9, default="2026-2027")
    created = models.DateTimeField("Inscrit le", auto_now_add=True)

    class Meta:
        unique_together = ("student", "classroom", "academic_year")
        verbose_name = "inscription"
        verbose_name_plural = "inscriptions"

    def __str__(self):
        return f"{self.student} → {self.classroom} ({self.academic_year})"
