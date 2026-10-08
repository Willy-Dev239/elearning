from django.db.models import Sum
from django.urls import reverse


def dashboard_callback(request, context):
    from accounts.models import User
    from courses.models import Course, Lesson
    from payments.models import Payment
    from quizzes.models import Quiz
    from schools.models import Classroom

    paid = Payment.objects.filter(status="PAID")
    total = paid.aggregate(s=Sum("amount"))["s"] or 0
    link = lambda n: reverse(f"admin:{n}_changelist")
    context.update({
        "stats": [
            {"label": "Étudiants", "value": User.objects.filter(role="STUDENT").count(), "href": link("accounts_user") + "?role__exact=STUDENT"},
            {"label": "Enseignants", "value": User.objects.filter(role="TEACHER").count(), "href": link("accounts_user") + "?role__exact=TEACHER"},
            {"label": "Classes", "value": Classroom.objects.count(), "href": link("schools_classroom")},
            {"label": "Cours", "value": Course.objects.count(), "href": link("courses_course")},
            {"label": "Leçons", "value": Lesson.objects.count(), "href": link("courses_lesson")},
            {"label": "Quiz", "value": Quiz.objects.count(), "href": link("quizzes_quiz")},
            {"label": "Paiements reçus", "value": paid.count(), "href": link("payments_payment")},
            {"label": "Total encaissé", "value": f"{total:,.0f}".replace(",", " "), "href": link("payments_payment")},
        ],
        "recent_payments": Payment.objects.select_related("student", "fee")[:6],
    })
    return context
