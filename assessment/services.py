"""Moteur de correction : auto-correction des QCM, correction manuelle des réponses libres."""
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from academic.models import Enrollment, Grade

from .models import Answer, Attempt, Question


def auto_grade_answer(answer, question):
    if question.type == Question.Type.TEXT:
        if answer.text_answer.strip():
            answer.is_correct = None
            answer.points_awarded = None  # en attente de correction par l'enseignant
        else:
            answer.is_correct = False
            answer.points_awarded = Decimal("0")
        return
    selected = {c.id for c in answer.selected_choices.all()}
    correct = {c.id for c in question.choices.all() if c.is_correct}
    ok = bool(correct) and selected == correct
    answer.is_correct = ok
    answer.points_awarded = question.points if ok else Decimal("0")


def recompute_attempt(attempt):
    """Recalcule le score ; passe en GRADED quand plus aucune réponse n'attend de note."""
    answers = attempt.answers.all()
    pending = answers.filter(points_awarded__isnull=True).exists()
    attempt.score = answers.aggregate(s=Sum("points_awarded"))["s"] or Decimal("0")
    attempt.max_score = attempt.quiz.total_points
    attempt.status = Attempt.Status.SUBMITTED if pending else Attempt.Status.GRADED
    attempt.save()
    if attempt.status == Attempt.Status.GRADED:
        sync_grade(attempt)
    return attempt


def sync_grade(attempt):
    """Reporte la meilleure note du quiz dans le relevé de notes (module Academic)."""
    quiz = attempt.quiz
    if not quiz.counts_for_grade or not attempt.max_score:
        return
    enrollment = Enrollment.objects.filter(student=attempt.student, course=quiz.course).first()
    if enrollment is None:
        return
    best = (
        quiz.attempts.filter(student=attempt.student, status=Attempt.Status.GRADED)
        .order_by("-score")
        .first()
    )
    Grade.objects.update_or_create(
        enrollment=enrollment,
        source_ref=f"quiz:{quiz.id}",
        defaults={
            "title": quiz.title,
            "score": best.score,
            "max_score": best.max_score,
            "coefficient": quiz.coefficient,
            "graded_by": quiz.created_by,
        },
    )


@transaction.atomic
def submit_attempt(attempt, answers_data):
    quiz = attempt.quiz
    questions = {q.id: q for q in quiz.questions.prefetch_related("choices")}

    provided = {}
    for item in answers_data:
        if item["question"] not in questions:
            raise ValidationError(f"La question {item['question']} n'appartient pas à ce quiz.")
        provided[item["question"]] = item

    for qid, question in questions.items():
        item = provided.get(qid, {})
        valid_choice_ids = {c.id for c in question.choices.all()}
        chosen = set(item.get("selected_choices", []))
        if not chosen <= valid_choice_ids:
            raise ValidationError(f"Choix invalide pour la question {qid}.")
        answer, _ = Answer.objects.get_or_create(attempt=attempt, question=question)
        answer.text_answer = item.get("text_answer", "")
        answer.save()
        answer.selected_choices.set(chosen)
        auto_grade_answer(answer, question)
        answer.save()

    attempt.submitted_at = timezone.now()
    return recompute_attempt(attempt)
