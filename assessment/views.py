from datetime import timedelta

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from academic.access import accessible_course_ids
from accounts.models import User
from core.permissions import IsOwnerTeacherOrAdmin, IsStudent, IsTeacherOrAdmin

from .models import Answer, Attempt, Question, Quiz
from .serializers import (
    AttemptSerializer,
    ManualGradeSerializer,
    QuestionSerializer,
    QuizDetailSerializer,
    QuizSerializer,
    SubmitSerializer,
)
from .services import recompute_attempt, submit_attempt

WRITE_ACTIONS = ("create", "update", "partial_update", "destroy")
GRACE = timedelta(minutes=2)  # tolérance réseau mobile


class QuizViewSet(viewsets.ModelViewSet):
    """Quiz et devoirs. Les étudiants ne voient jamais les bonnes réponses."""

    filterset_fields = ["course", "kind", "is_published"]
    search_fields = ["title"]
    ordering_fields = ["created_at", "due_date"]

    def get_serializer_class(self):
        return QuizDetailSerializer if self.action == "retrieve" else QuizSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Quiz.objects.none()
        user = self.request.user
        qs = Quiz.objects.select_related("course")
        if user.role == User.Role.ADMIN:
            return qs
        if user.role == User.Role.TEACHER:
            return qs.filter(course__teacher=user)
        return qs.filter(is_published=True, course_id__in=accessible_course_ids(user))

    def get_permissions(self):
        if self.action in WRITE_ACTIONS:
            return [IsTeacherOrAdmin(), IsOwnerTeacherOrAdmin()]
        if self.action == "start":
            return [IsStudent()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema(request=None, responses=AttemptSerializer)
    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        """Démarre (ou reprend) une tentative : retourne les questions sans les corrections."""
        quiz = self.get_object()
        now = timezone.now()
        if quiz.available_from and now < quiz.available_from:
            raise ValidationError("Ce quiz n'est pas encore disponible.")
        if quiz.due_date and now > quiz.due_date:
            raise ValidationError("La date limite est dépassée.")

        current = Attempt.objects.filter(
            quiz=quiz, student=request.user, status=Attempt.Status.IN_PROGRESS
        ).first()
        if current:
            return Response(AttemptSerializer(current, context={"request": request}).data)

        used = Attempt.objects.filter(quiz=quiz, student=request.user).count()
        if used >= quiz.max_attempts:
            raise ValidationError("Nombre maximal de tentatives atteint.")
        if not quiz.questions.exists():
            raise ValidationError("Ce quiz ne contient aucune question.")

        attempt = Attempt.objects.create(quiz=quiz, student=request.user)
        return Response(
            AttemptSerializer(attempt, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class QuestionViewSet(viewsets.ModelViewSet):
    """Gestion des questions (enseignant/admin)."""

    serializer_class = QuestionSerializer
    permission_classes = [IsTeacherOrAdmin, IsOwnerTeacherOrAdmin]
    filterset_fields = ["quiz", "type"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Question.objects.none()
        user = self.request.user
        qs = Question.objects.select_related("quiz__course").prefetch_related("choices")
        if user.role == User.Role.ADMIN:
            return qs
        return qs.filter(quiz__course__teacher=user)


class AttemptViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Tentatives : soumission, résultats et correction manuelle."""

    serializer_class = AttemptSerializer
    filterset_fields = ["quiz", "status", "student"]
    ordering_fields = ["started_at", "score"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Attempt.objects.none()
        user = self.request.user
        qs = Attempt.objects.select_related("quiz__course", "student")
        if user.role == User.Role.ADMIN:
            return qs
        if user.role == User.Role.TEACHER:
            return qs.filter(quiz__course__teacher=user)
        return qs.filter(student=user)

    def get_permissions(self):
        if self.action == "submit":
            return [IsStudent()]
        if self.action == "grade":
            return [IsTeacherOrAdmin(), IsOwnerTeacherOrAdmin()]
        return [IsAuthenticated()]

    @extend_schema(request=SubmitSerializer, responses=AttemptSerializer)
    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Soumet les réponses ; les QCM sont corrigés automatiquement."""
        attempt = self.get_object()
        if attempt.status != Attempt.Status.IN_PROGRESS:
            raise ValidationError("Cette tentative est déjà soumise.")
        quiz = attempt.quiz
        now = timezone.now()
        if quiz.duration_minutes and now > attempt.started_at + timedelta(minutes=quiz.duration_minutes) + GRACE:
            raise ValidationError("Temps écoulé.")
        if quiz.due_date and now > quiz.due_date + GRACE and attempt.started_at > quiz.due_date:
            raise ValidationError("La date limite est dépassée.")

        serializer = SubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attempt = submit_attempt(attempt, serializer.validated_data["answers"])
        return Response(AttemptSerializer(attempt, context={"request": request}).data)

    @extend_schema(request=ManualGradeSerializer, responses=AttemptSerializer)
    @action(detail=True, methods=["post"])
    def grade(self, request, pk=None):
        """Correction manuelle des réponses libres par l'enseignant."""
        attempt = self.get_object()
        if attempt.status == Attempt.Status.IN_PROGRESS:
            raise ValidationError("La tentative n'est pas encore soumise.")
        serializer = ManualGradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        answers = {
            a.id: a
            for a in Answer.objects.filter(attempt=attempt).select_related("question")
        }
        for item in serializer.validated_data["answers"]:
            answer = answers.get(item["id"])
            if answer is None:
                raise ValidationError(f"Réponse {item['id']} introuvable dans cette tentative.")
            if item["points_awarded"] > answer.question.points:
                raise ValidationError(
                    f"Réponse {answer.id} : maximum {answer.question.points} points."
                )
            answer.points_awarded = item["points_awarded"]
            answer.feedback = item["feedback"]
            answer.is_correct = item["points_awarded"] == answer.question.points
            answer.save()

        attempt = recompute_attempt(attempt)
        return Response(AttemptSerializer(attempt, context={"request": request}).data)
