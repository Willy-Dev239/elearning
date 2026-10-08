from datetime import date, timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from accounts.models import User
from courses.models import Course, Lesson
from payments.models import Fee
from quizzes.models import Choice, Question, Quiz
from schools.models import Classroom, Enrollment, School


class Command(BaseCommand):
    help = "Crée des données de démonstration"

    def handle(self, *args, **opts):
        def user(username, pwd, role, first, last):
            u, new = User.objects.get_or_create(username=username, defaults=dict(
                role=role, first_name=first, last_name=last, email=f"{username}@example.com"))
            if new:
                u.set_password(pwd)
                u.save()
            return u

        user("admin", "admin12345", "ADMIN", "Back", "Office")
        prof = user("prof", "prof12345", "TEACHER", "Jean", "Enseignant")
        stu = user("etudiant", "etud12345", "STUDENT", "Marie", "Étudiante")

        school, _ = School.objects.get_or_create(name="École Démo", defaults={"address": "Centre-ville"})
        room, _ = Classroom.objects.get_or_create(school=school, name="Licence 1")
        Enrollment.objects.get_or_create(student=stu, classroom=room)
        course, new = Course.objects.get_or_create(classroom=room, teacher=prof, title="Introduction à Python",
                                                   defaults={"description": "Bases du langage Python."})
        if new:
            lesson = Lesson(course=course, title="Support de cours (PDF/Texte)", kind="DOCUMENT")
            lesson.file.save("support.txt", ContentFile("Bienvenue au cours Python !\nVariables, boucles, fonctions."))
            quiz = Quiz.objects.create(course=course, title="Quiz 1 — Les bases", pass_mark=50)
            for i, (q, choices) in enumerate([
                ("Quel mot-clé définit une fonction ?", [("def", True), ("func", False), ("function", False)]),
                ("Quel type est [1, 2, 3] ?", [("list", True), ("tuple", False), ("dict", False)]),
            ]):
                question = Question.objects.create(quiz=quiz, text=q, order=i)
                for t, ok in choices:
                    Choice.objects.create(question=question, text=t, is_correct=ok)
        Fee.objects.get_or_create(classroom=room, title="Frais de scolarité — Trimestre 1",
                                  defaults={"amount": 150000, "due_date": date.today() + timedelta(days=30)})
        self.stdout.write(self.style.SUCCESS("Démo prête : admin/admin12345 · prof/prof12345 · etudiant/etud12345"))
