import hashlib
import hmac
import json
import shutil
import tempfile
from datetime import date, time

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase

from academic.models import AcademicYear, Course, Enrollment
from accounts.models import User
from billing.models import FeeStructure, Installment

TMP_MEDIA = tempfile.mkdtemp()
V1 = "/api/v1"


@override_settings(MEDIA_ROOT=TMP_MEDIA, MOBILE_MONEY_AUTO_CONFIRM=False)
class ApiFlowTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.admin = User.objects.create_superuser("admin", "a@x.bi", "Pass12345!")
        self.teacher = User .objects.create_user(
            "teach", "t@x.bi", "Pass12345!", role=User.Role.TEACHER, first_name="Claire"
        )
        self.student = User.objects.create_user(
            "stud", "s@x.bi", "Pass12345!", role=User.Role.STUDENT, first_name="Jean"
        )
        self.other_student = User.objects.create_user(
            "stud2", "s2@x.bi", "Pass12345!", role=User.Role.STUDENT
        )

    def login(self, user):
        self.client.force_authenticate(user=user)

    # ---------- Auth ----------
    def test_register_login_me_logout(self):
        self.client.force_authenticate(user=None)
        r = self.client.post(f"{V1}/auth/register/", {
            "username": "new", "email": "n@x.bi", "password": "Str0ngPass!2026",
            "first_name": "N", "last_name": "N",
        })
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(User.objects.get(username="new").role, "student")

        r = self.client.post(f"{V1}/auth/login/", {"username": "new", "password": "Str0ngPass!2026"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["user"]["role"], "student")
        access, refresh = r.data["access"], r.data["refresh"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        self.assertEqual(self.client.get(f"{V1}/auth/me/").data["username"], "new")
        self.assertEqual(self.client.post(f"{V1}/auth/logout/", {"refresh": refresh}).status_code, 204)

    def test_only_admin_manages_users(self):
        self.login(self.student)
        self.assertEqual(self.client.get(f"{V1}/users/").status_code, 403)
        self.login(self.admin)
        r = self.client.post(f"{V1}/users/", {
            "username": "t2", "email": "t2@x.bi", "password": "Str0ngPass!2026", "role": "teacher",
        })
        self.assertEqual(r.status_code, 201, r.data)

    # ---------- Academic ----------
    def _make_course(self, **kw):
        year = AcademicYear.objects.create(
            name="2026-2027", start_date=date(2026, 9, 1), end_date=date(2027, 6, 30), is_current=True
        )
        data = dict(code="C1", title="Cours 1", teacher=self.teacher, academic_year=year, credits=2)
        data.update(kw)
        return Course.objects.create(**data)

    def test_course_enroll_timetable_grades_transcript(self):
        # l'enseignant crée un cours
        self.login(self.teacher)
        r = self.client.post(f"{V1}/academic/courses/", {"code": "INF1", "title": "Django", "credits": 3})
        self.assertEqual(r.status_code, 201, r.data)
        course_id = r.data["id"]
        self.assertEqual(r.data["teacher"], self.teacher.id)

        r = self.client.post(f"{V1}/academic/timetable/", {
            "course": course_id, "weekday": 0, "start_time": "08:00", "end_time": "10:00", "room": "A1",
        })
        self.assertEqual(r.status_code, 201, r.data)

        # l'étudiant s'inscrit et voit l'emploi du temps
        self.login(self.student)
        self.assertEqual(self.client.post(f"{V1}/academic/courses/{course_id}/enroll/").status_code, 201)
        self.assertEqual(self.client.get(f"{V1}/academic/timetable/").data["count"], 1)
        # l'autre étudiant n'a rien
        self.login(self.other_student)
        self.assertEqual(self.client.get(f"{V1}/academic/timetable/").data["count"], 0)

        # saisie des notes en lot
        self.login(self.teacher)
        r = self.client.post(f"{V1}/academic/grades/bulk/", {
            "course": course_id, "title": "Examen", "max_score": 20, "coefficient": 2,
            "grades": [{"student": self.student.id, "score": "15.5"}],
        }, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        # note > max refusée
        r = self.client.post(f"{V1}/academic/grades/bulk/", {
            "course": course_id, "title": "X", "max_score": 20,
            "grades": [{"student": self.student.id, "score": "25"}],
        }, format="json")
        self.assertEqual(r.status_code, 400)

        # relevé de notes de l'étudiant
        self.login(self.student)
        r = self.client.get(f"{V1}/academic/transcript/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["general_average"], 15.5)

    def test_teacher_cannot_touch_other_teacher_course(self):
        other = User.objects.create_user("t3", "t3@x.bi", "Pass12345!", role=User.Role.TEACHER)
        course = self._make_course(teacher=other)
        self.login(self.teacher)
        r = self.client.patch(f"{V1}/academic/courses/{course.id}/", {"title": "Hack"})
        self.assertEqual(r.status_code, 403)

    # ---------- Media + paiement ----------
    def test_paid_course_media_requires_payment_and_supports_range(self):
        course = self._make_course(price=25000)
        Enrollment.objects.create(student=self.student, course=course)

        self.login(self.teacher)
        content = b"0123456789" * 100
        r = self.client.post(f"{V1}/media/materials/", {
            "course": course.id, "title": "Intro", "kind": "video",
            "file": SimpleUploadedFile("intro.mp4", content, content_type="video/mp4"),
        }, format="multipart")
        self.assertEqual(r.status_code, 201, r.data)
        material_id = r.data["id"]
        # mauvaise extension refusée
        r = self.client.post(f"{V1}/media/materials/", {
            "course": course.id, "title": "Bad", "kind": "video",
            "file": SimpleUploadedFile("virus.exe", b"x"),
        }, format="multipart")
        self.assertEqual(r.status_code, 400)

        # étudiant inscrit mais n'ayant pas payé : accès refusé
        self.login(self.student)
        self.assertEqual(self.client.get(f"{V1}/media/materials/{material_id}/stream/").status_code, 404)

        # paiement Mobile Money (en attente puis confirmé par webhook signé)
        r = self.client.post(f"{V1}/billing/payments/", {
            "course": course.id, "provider": "lumicash", "phone_number": "79 123 456",
        })
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data["status"], "pending")
        self.assertEqual(r.data["phone_number"], "+25779123456")
        reference = r.data["reference"]
        self.assertEqual(self.client.get(f"{V1}/media/materials/{material_id}/stream/").status_code, 404)

        body = json.dumps({"reference": reference, "status": "success", "transaction_id": "TX1"})
        self.client.force_authenticate(user=None)
        bad = self.client.post(f"{V1}/billing/webhook/", body, content_type="application/json",
                               HTTP_X_SIGNATURE="nope")
        self.assertEqual(bad.status_code, 401)
        sig = hmac.new(b"change-me-webhook-secret", body.encode(), hashlib.sha256).hexdigest()
        ok = self.client.post(f"{V1}/billing/webhook/", body, content_type="application/json",
                              HTTP_X_SIGNATURE=sig)
        self.assertEqual(ok.status_code, 200, ok.data)

        # accès débloqué + streaming par plage
        self.login(self.student)
        full = self.client.get(f"{V1}/media/materials/{material_id}/stream/")
        self.assertEqual(full.status_code, 200)
        self.assertEqual(b"".join(full.streaming_content), content)
        part = self.client.get(f"{V1}/media/materials/{material_id}/stream/", HTTP_RANGE="bytes=10-19")
        self.assertEqual(part.status_code, 206)
        self.assertEqual(part["Content-Range"], "bytes 10-19/1000")
        self.assertEqual(b"".join(part.streaming_content), b"0123456789")

        # progression
        r = self.client.post(f"{V1}/media/materials/{material_id}/progress/",
                             {"completed": True, "last_position_seconds": 42})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get(f"{V1}/media/courses/{course.id}/progress/").data["percent"], 100.0)

        # un autre étudiant non inscrit ne voit pas le fichier
        self.login(self.other_student)
        self.assertEqual(self.client.get(f"{V1}/media/materials/{material_id}/stream/").status_code, 404)

    def test_tuition_installments_my_account_and_tracking(self):
        course = self._make_course()
        Enrollment.objects.create(student=self.student, course=course)
        fee = FeeStructure.objects.create(title="Scolarité")
        i1 = Installment.objects.create(fee=fee, label="T1", amount=100000, due_date=date(2030, 1, 1))
        Installment.objects.create(fee=fee, label="T2", amount=50000, due_date=date(2030, 6, 1))

        self.login(self.student)
        r = self.client.post(f"{V1}/billing/payments/", {
            "installment": i1.id, "provider": "ecocash", "phone_number": "61000000",
        })
        self.assertEqual(r.status_code, 201, r.data)
        # double cible refusée
        r2 = self.client.post(f"{V1}/billing/payments/", {
            "installment": i1.id, "course": course.id, "provider": "ecocash", "phone_number": "61000000",
        })
        self.assertEqual(r2.status_code, 400)

        # confirmation manuelle par l'admin
        self.login(self.admin)
        self.assertEqual(self.client.post(f"{V1}/billing/payments/{r.data['id']}/confirm/").status_code, 200)

        self.login(self.student)
        acct = self.client.get(f"{V1}/billing/my-account/").data
        self.assertEqual(acct["total_due"], "150000.00")
        self.assertEqual(acct["total_paid"], "100000.00")
        self.assertEqual(acct["balance"], "50000.00")

        self.login(self.teacher)
        tr = self.client.get(f"{V1}/billing/tracking/").data
        self.assertEqual(tr["count"], 1)
        self.assertEqual(tr["results"][0]["status"], "partial")

    # ---------- Assessment ----------
    def test_quiz_autograding_and_manual_grading(self):
        course = self._make_course()
        Enrollment.objects.create(student=self.student, course=course)

        self.login(self.teacher)
        quiz = self.client.post(f"{V1}/assessment/quizzes/", {
            "course": course.id, "title": "Quiz 1", "is_published": True, "max_attempts": 2,
        }).data
        qid = quiz["id"]
        single = self.client.post(f"{V1}/assessment/questions/", {
            "quiz": qid, "text": "REST ?", "type": "single", "points": 2,
            "choices": [{"text": "Bon", "is_correct": True}, {"text": "Faux", "is_correct": False}],
        }, format="json")
        self.assertEqual(single.status_code, 201, single.data)
        multi = self.client.post(f"{V1}/assessment/questions/", {
            "quiz": qid, "text": "Verbes ?", "type": "multiple", "points": 2,
            "choices": [{"text": "GET", "is_correct": True}, {"text": "POST", "is_correct": True},
                        {"text": "SEND", "is_correct": False}],
        }, format="json")
        text = self.client.post(f"{V1}/assessment/questions/", {
            "quiz": qid, "text": "Expliquez", "type": "text", "points": 4,
        }, format="json")
        self.assertEqual(text.status_code, 201, text.data)
        # une question à choix unique avec 2 bonnes réponses est refusée
        bad = self.client.post(f"{V1}/assessment/questions/", {
            "quiz": qid, "text": "?", "type": "single",
            "choices": [{"text": "a", "is_correct": True}, {"text": "b", "is_correct": True}],
        }, format="json")
        self.assertEqual(bad.status_code, 400)

        good_single = next(c["id"] for c in single.data["choices"] if c["is_correct"])
        good_multi = [c["id"] for c in multi.data["choices"] if c["is_correct"]]

        # l'étudiant démarre : les bonnes réponses ne fuient pas
        self.login(self.student)
        started = self.client.post(f"{V1}/assessment/quizzes/{qid}/start/")
        self.assertEqual(started.status_code, 201, started.data)
        self.assertNotIn("is_correct", json.dumps(started.data))
        detail = self.client.get(f"{V1}/assessment/quizzes/{qid}/")
        self.assertNotIn("is_correct", json.dumps(detail.data))

        attempt_id = started.data["id"]
        res = self.client.post(f"{V1}/assessment/attempts/{attempt_id}/submit/", {
            "answers": [
                {"question": single.data["id"], "selected_choices": [good_single]},
                {"question": multi.data["id"], "selected_choices": good_multi},
                {"question": text.data["id"], "text_answer": "PUT remplace, PATCH modifie."},
            ]
        }, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["status"], "submitted")  # réponse libre en attente
        self.assertIsNone(res.data["score"])

        # l'enseignant corrige la réponse libre
        self.login(self.teacher)
        attempt = self.client.get(f"{V1}/assessment/attempts/{attempt_id}/").data
        free = next(a for a in attempt["answers"] if a["question_type"] == "text")
        res = self.client.post(f"{V1}/assessment/attempts/{attempt_id}/grade/", {
            "answers": [{"id": free["id"], "points_awarded": "3", "feedback": "Bien"}]
        }, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["status"], "graded")
        self.assertEqual(float(res.data["score"]), 7.0)

        # la note est reportée dans le relevé de notes
        self.login(self.student)
        tr = self.client.get(f"{V1}/academic/transcript/").data
        self.assertEqual(tr["courses"][0]["grades"][0]["score"], 7.0)
        self.assertEqual(tr["courses"][0]["grades"][0]["max_score"], 8.0)

        # 2e soumission refusée
        again = self.client.post(f"{V1}/assessment/attempts/{attempt_id}/submit/", {"answers": []}, format="json")
        self.assertEqual(again.status_code, 400)

    # ---------- Documentation ----------
    def test_openapi_schema_builds(self):
        self.client.force_authenticate(user=None)
        r = self.client.get("/api/schema/")
        self.assertEqual(r.status_code, 200)
