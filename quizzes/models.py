from django.conf import settings
from django.db import models


class Quiz(models.Model):
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="quizzes", verbose_name="Cours")
    title = models.CharField("Titre", max_length=200)
    description = models.TextField("Description", blank=True)
    pass_mark = models.PositiveIntegerField("Seuil de réussite (%)", default=50)

    class Meta:
        verbose_name = "quiz"
        verbose_name_plural = "quiz"

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions", verbose_name="Quiz")
    text = models.CharField("Question", max_length=500)
    order = models.PositiveIntegerField("Ordre", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "question"
        verbose_name_plural = "questions"

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices", verbose_name="Question")
    text = models.CharField("Réponse proposée", max_length=300)
    is_correct = models.BooleanField("Bonne réponse", default=False)

    class Meta:
        verbose_name = "choix"
        verbose_name_plural = "choix"

    def __str__(self):
        return self.text


class Attempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts", verbose_name="Quiz")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts", verbose_name="Étudiant")
    score = models.PositiveIntegerField("Bonnes réponses")
    total = models.PositiveIntegerField("Nombre de questions")
    created = models.DateTimeField("Passé le", auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "résultat"
        verbose_name_plural = "résultats"

    def __str__(self):
        return f"{self.student} — {self.quiz} ({self.score}/{self.total})"

    @property
    def percent(self):
        return round(100 * self.score / self.total) if self.total else 0

    @property
    def passed(self):
        return self.percent >= self.quiz.pass_mark
