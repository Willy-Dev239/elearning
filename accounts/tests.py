from io import StringIO

from rest_framework.test import APITestCase
from django.core.management import call_command


class FlowTest(APITestCase):
    def setUp(self):
        call_command("seed_demo", stdout=StringIO())

    def login(self, u, p):
        r = self.client.post("/api/auth/login/", {"username": u, "password": p}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + r.data["access"])
        return r.data["access"]

    def test_student_flow(self):
        tok = self.login("etudiant", "etud12345")
        course = self.client.get("/api/courses/").data[0]
        lesson = self.client.get(f"/api/lessons/?course={course['id']}").data[0]
        self.assertNotIn("file", lesson)
        self.client.credentials()
        r = self.client.get(f"{lesson['stream_url']}?token={tok}", HTTP_RANGE="bytes=0-4")
        self.assertEqual(r.status_code, 206)
        self.assertEqual(b"".join(r.streaming_content), b"Bienv")
        self.login("etudiant", "etud12345")
        quiz = self.client.get("/api/quizzes/").data[0]
        self.assertNotIn("is_correct", quiz["questions"][0]["choices"][0])
        self.assertEqual(self.client.post("/api/courses/", {}, format="json").status_code, 403)
        from quizzes.models import Choice
        ans = {str(q["id"]): Choice.objects.get(question_id=q["id"], is_correct=True).id for q in quiz["questions"]}
        r = self.client.post(f"/api/quizzes/{quiz['id']}/attempt/", {"answers": ans}, format="json")
        self.assertEqual((r.data["score"], r.data["passed"]), (2, True))
        fee = self.client.get("/api/fees/").data[0]
        r = self.client.post("/api/payments/", {"fee": fee["id"], "method": "MOBILE_MONEY", "phone": "79000000", "amount": "50000"}, format="json")
        self.assertEqual(r.data["status"], "PAID")
        self.assertEqual(self.client.get("/api/fees/").data[0]["remaining"], 100000)
        self.assertEqual(self.client.post("/api/payments/", {"fee": fee["id"], "amount": "999999"}, format="json").status_code, 400)

    def test_teacher_and_admin(self):
        self.login("prof", "prof12345")
        c = self.client.get("/api/courses/").data[0]
        r = self.client.post("/api/quizzes/", {"course": c["id"], "title": "Q2", "questions": [
            {"text": "1+1 ?", "choices": [{"text": "2", "is_correct": True}, {"text": "3", "is_correct": False}]}]}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.client.get("/api/stats/").status_code, 403)
        self.login("admin", "admin12345")
        self.assertEqual(self.client.get("/api/stats/").data["quizzes"], 2)
