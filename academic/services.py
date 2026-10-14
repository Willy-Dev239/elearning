"""Calcul des moyennes et du relevé de notes."""
from .models import Enrollment


def weighted_average(grades):
    """Moyenne pondérée ramenée sur 20."""
    total_coef = sum(float(g.coefficient) for g in grades)
    if not total_coef:
        return None
    total = sum((float(g.score) / float(g.max_score) * 20) * float(g.coefficient) for g in grades)
    return round(total / total_coef, 2)


def compute_transcript(student, teacher=None):
    """Relevé de notes d'un étudiant. Si `teacher` est fourni, limité à ses cours."""
    enrollments = (
        Enrollment.objects.filter(student=student)
        .exclude(status=Enrollment.Status.DROPPED)
        .select_related("course")
        .prefetch_related("grades")
    )
    if teacher is not None:
        enrollments = enrollments.filter(course__teacher=teacher)

    rows, weighted_sum, credits_sum = [], 0.0, 0
    for enrollment in enrollments:
        grades = list(enrollment.grades.all())
        average = weighted_average(grades)
        course = enrollment.course
        rows.append(
            {
                "course_id": course.id,
                "code": course.code,
                "title": course.title,
                "credits": course.credits,
                "average": average,
                "grades": [
                    {
                        "id": g.id,
                        "title": g.title,
                        "score": float(g.score),
                        "max_score": float(g.max_score),
                        "score_on_20": g.score_on_20,
                        "coefficient": float(g.coefficient),
                        "comment": g.comment,
                        "date": g.created_at.date().isoformat(),
                    }
                    for g in grades
                ],
            }
        )
        if average is not None:
            weighted_sum += average * course.credits
            credits_sum += course.credits

    return {
        "student": {
            "id": student.id,
            "name": student.get_full_name() or student.username,
        },
        "courses": rows,
        "general_average": round(weighted_sum / credits_sum, 2) if credits_sum else None,
    }
