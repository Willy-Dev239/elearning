from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Étudiant"
        TEACHER = "TEACHER", "Enseignant"
        ADMIN = "ADMIN", "Back office"

    role = models.CharField("Rôle", max_length=10, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField("Téléphone", max_length=20, blank=True)

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        if self.role == self.Role.ADMIN:  # le back office a accès à toute l'administration
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)
