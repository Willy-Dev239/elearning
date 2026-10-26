from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from core.models import TimeStampedModel
class AcademicYear(TimeStampedModel):
    name = models.CharField(max_length=20, unique=True, help_text="ex. 2026-2027")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_current:
            AcademicYear.objects.exclude(pk=self.pk).update(is_current=False)

    def __str__(self):
        return self.name


class Course(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="courses_taught",
        limit_choices_to={"role": "teacher"},
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.PROTECT, related_name="courses", null=True, blank=True
    )
    credits = models.PositiveSmallIntegerField(default=1)
    # price > 0  =>  module payant (accès conditionné à un paiement Mobile Money)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    @property
    def is_paid(self):
        return self.price > 0

    def __str__(self):
        return f"{self.code} — {self.title}"


class Enrollment(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Actif"
        COMPLETED = "completed", "Terminé"
        DROPPED = "dropped", "Abandonné"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        limit_choices_to={"role": "student"},
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-enrolled_at"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_student_course")
        ]

    def __str__(self):
        return f"{self.student} → {self.course.code}"


class TimetableSlot(TimeStampedModel):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Lundi"
        TUESDAY = 1, "Mardi"
        WEDNESDAY = 2, "Mercredi"
        THURSDAY = 3, "Jeudi"
        FRIDAY = 4, "Vendredi"
        SATURDAY = 5, "Samedi"
        SUNDAY = 6, "Dimanche"

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="slots")
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=60, blank=True)

    class Meta:
        ordering = ["weekday", "start_time"]

    def __str__(self):
        return f"{self.course.code} {self.get_weekday_display()} {self.start_time:%H:%M}"


class Grade(TimeStampedModel):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="grades")
    title = models.CharField(max_length=120, help_text="ex. Examen partiel, TP1...")
    score = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=20)
    coefficient = models.DecimalField(max_digits=4, decimal_places=2, default=1)
    comment = models.CharField(max_length=255, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    # Renseigné quand la note provient automatiquement d'un quiz (ex. "quiz:12")
    source_ref = models.CharField(max_length=50, blank=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def score_on_20(self):
        if not self.max_score:
            return None
        return round(float(self.score) / float(self.max_score) * 20, 2)

    def __str__(self):
        return f"{self.title}: {self.score}/{self.max_score}"
class SchoolClass(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.SET_NULL, null=True, blank=True, related_name="classes"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

