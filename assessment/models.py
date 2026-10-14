from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum

from core.models import TimeStampedModel


class Quiz(TimeStampedModel):
    class Kind(models.TextChoices):
        QUIZ = "quiz", "Quiz"
        ASSIGNMENT = "assignment", "Devoir"

    course = models.ForeignKey("academic.Course", on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.QUIZ)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    max_attempts = models.PositiveSmallIntegerField(default=1)
    available_from = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    show_corrections = models.BooleanField(default=True)
    counts_for_grade = models.BooleanField(
        default=True, help_text="La note est reportée automatiquement dans le relevé de notes."
    )
    coefficient = models.DecimalField(max_digits=4, decimal_places=2, default=1)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "quizzes"

    @property
    def total_points(self):
        return self.questions.aggregate(s=Sum("points"))["s"] or Decimal("0")

    def __str__(self):
        return self.title


class Question(TimeStampedModel):
    class Type(models.TextChoices):
        SINGLE = "single", "Choix unique"
        MULTIPLE = "multiple", "Choix multiples"
        TRUE_FALSE = "true_false", "Vrai / Faux"
        TEXT = "text", "Réponse libre (correction manuelle)"

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    type = models.CharField(max_length=12, choices=Type.choices, default=Type.SINGLE)
    points = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.text[:60]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.text


class Attempt(TimeStampedModel):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "En cours"
        SUBMITTED = "submitted", "Soumis (correction en attente)"
        GRADED = "graded", "Corrigé"

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts"
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.IN_PROGRESS)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    max_score = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    class Meta:
        ordering = ["-started_at"]


class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    selected_choices = models.ManyToManyField(Choice, blank=True, related_name="+")
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    points_awarded = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["attempt", "question"], name="unique_attempt_question")
        ]
