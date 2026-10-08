from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsStudent, read_or
from courses.views import visible_courses
from .models import Attempt, Quiz
from .serializers import AttemptSerializer, QuizSerializer


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [read_or("TEACHER", "ADMIN")]

    def get_queryset(self):
        qs = Quiz.objects.filter(course__in=visible_courses(self.request.user)) \
            .prefetch_related("questions__choices")
        course = self.request.query_params.get("course")
        return qs.filter(course_id=course) if course else qs

    @action(detail=True, methods=["post"], permission_classes=[IsStudent])
    def attempt(self, request, pk=None):
        """Body : {"answers": {"<question_id>": <choice_id>, ...}} → correction automatique."""
        quiz = self.get_object()
        answers = request.data.get("answers") or {}
        questions = list(quiz.questions.all())
        score = 0
        for q in questions:
            correct = {str(c.id) for c in q.choices.all() if c.is_correct}
            if str(answers.get(str(q.id))) in correct:
                score += 1
        att = Attempt.objects.create(quiz=quiz, student=request.user, score=score, total=len(questions))
        return Response(AttemptSerializer(att).data, status=201)


class AttemptViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AttemptSerializer

    def get_queryset(self):
        u = self.request.user
        qs = Attempt.objects.select_related("quiz", "student")
        if u.role == "ADMIN":
            return qs
        if u.role == "TEACHER":
            return qs.filter(quiz__course__teacher=u)
        return qs.filter(student=u)
