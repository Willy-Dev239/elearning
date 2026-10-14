"""Données de démonstration pour l'équipe mobile : python manage.py seed_demo"""
from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from academic.models import AcademicYear, Course, Enrollment, TimetableSlot
from accounts.models import User
from assessment.models import Choice, Question, Quiz
from billing.models import FeeStructure, Installment

PASSWORD = "Demo12345!"


class Command(BaseCommand):
    help = "Crée des comptes et données de démonstration (idempotent)."

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            username="admin", defaults={"email": "admin@school.bi", "is_staff": True, "is_superuser": True}
        )
        if created:
            admin.set_password(PASSWORD)
            admin.save()

        def make_user(username, role, first, last, phone):
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@school.bi", "role": role,
                    "first_name": first, "last_name": last, "phone": phone,
                },
            )
            if created:
                user.set_password(PASSWORD)
                user.save()
            return user

        teacher = make_user("teacher1", User.Role.TEACHER, "Claire", "Ndayisenga", "+25779000001")
        student = make_user("student1", User.Role.STUDENT, "Jean", "Niyonkuru", "+25779000002")
        make_user("student2", User.Role.STUDENT, "Aline", "Irakoze", "+25779000003")

        year, _ = AcademicYear.objects.get_or_create(
            name="2026-2027",
            defaults={"start_date": date(2026, 9, 1), "end_date": date(2027, 6, 30), "is_current": True},
        )
        django_course, _ = Course.objects.get_or_create(
            code="INF301",
            defaults={"title": "Développement Web avec Django", "teacher": teacher,
                      "academic_year": year, "credits": 4, "price": 0,
                      "description": "API REST, JWT, bases de données."},
        )
        premium, _ = Course.objects.get_or_create(
            code="INF402",
            defaults={"title": "Architecture Microservices (module payant)", "teacher": teacher,
                      "academic_year": year, "credits": 3, "price": Decimal("25000"),
                      "description": "Module payant via Mobile Money."},
        )
        Enrollment.objects.get_or_create(student=student, course=django_course)
        Enrollment.objects.get_or_create(student=student, course=premium)

        TimetableSlot.objects.get_or_create(
            course=django_course, weekday=0, start_time=time(8, 0),
            defaults={"end_time": time(10, 0), "room": "Salle A1"},
        )
        TimetableSlot.objects.get_or_create(
            course=django_course, weekday=2, start_time=time(14, 0),
            defaults={"end_time": time(16, 0), "room": "Labo 2"},
        )

        fee, fee_created = FeeStructure.objects.get_or_create(
            title="Frais de scolarité 2026-2027", defaults={"academic_year": year}
        )
        if fee_created:
            today = date.today()
            for i, amount in enumerate((150000, 150000, 100000), start=1):
                Installment.objects.create(
                    fee=fee, label=f"Tranche {i}", amount=amount,
                    due_date=today + timedelta(days=60 * i), order=i,
                )

        quiz, quiz_created = Quiz.objects.get_or_create(
            course=django_course, title="Quiz 1 — Bases de REST",
            defaults={"created_by": teacher, "is_published": True,
                      "duration_minutes": 15, "max_attempts": 2,
                      "due_date": timezone.now() + timedelta(days=30)},
        )
        if quiz_created:
            q1 = Question.objects.create(quiz=quiz, text="Que signifie REST ?", type="single", points=2, position=1)
            for text, ok in (("Representational State Transfer", True), ("Remote Server Transfer", False)):
                Choice.objects.create(question=q1, text=text, is_correct=ok)
            q2 = Question.objects.create(quiz=quiz, text="Quels sont des verbes HTTP ?", type="multiple", points=2, position=2)
            for text, ok in (("GET", True), ("POST", True), ("SEND", False)):
                Choice.objects.create(question=q2, text=text, is_correct=ok)
            q3 = Question.objects.create(quiz=quiz, text="PUT et PATCH : quelle différence ?", type="text", points=4, position=3)

        self.stdout.write(self.style.SUCCESS("Données de démonstration prêtes."))
        self.stdout.write(f"  admin / teacher1 / student1 / student2  —  mot de passe : {PASSWORD}")
