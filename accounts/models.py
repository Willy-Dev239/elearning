from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Étudiant"
        TEACHER = "teacher", "Enseignant"
        ADMIN = "admin", "Administrateur"

    email = models.EmailField("email", unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True)
    title = models.CharField("titre", max_length=20, blank=True)  # Dr, MSc... (enseignant/admin)
    class_name = models.CharField("classe", max_length=100, blank=True)  # étudiant
    academic_year = models.CharField("année scolaire", max_length=20, blank=True)  # étudiant

    class Meta:
        ordering = ["username"]

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"