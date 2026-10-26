from django.db import transaction
from django.db.models import Count, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from core.permissions import (
    IsAdmin,
    IsOwnerTeacherOrAdmin,
    IsStudent,
    IsTeacherOrAdmin,
)

from .models import AcademicYear, Course, Enrollment, Grade, SchoolClass, TimetableSlot
from .serializers import (
    AcademicYearSerializer,
    BulkGradeSerializer,
    CourseSerializer,
    EnrollmentSerializer,
    GradeSerializer,
    SchoolClassSerializer,
    TimetableSlotSerializer,
)
from .services import compute_transcript

WRITE_ACTIONS = ("create", "update", "partial_update", "destroy")


class SchoolClassViewSet(viewsets.ModelViewSet):
    queryset = SchoolClass.objects.all()
    serializer_class = SchoolClassSerializer

    def get_permissions(self):
        return [IsAdmin()] if self.action in WRITE_ACTIONS else [IsAuthenticated()]
class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    filterset_fields = ["is_current"]

    def get_permissions(self):
        if self.action in WRITE_ACTIONS:
            return [IsAdmin()]
        return [IsAuthenticated()]


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    filterset_fields = ["academic_year", "teacher", "is_published"]
    search_fields = ["code", "title", "description"]
    ordering_fields = ["code", "title", "created_at", "price"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Course.objects.none()
        user = self.request.user
        qs = Course.objects.select_related("teacher", "academic_year").annotate(
            active_enrollments=Count(
                "enrollments",
                filter=Q(enrollments__status=Enrollment.Status.ACTIVE),
                distinct=True,
            )
        )
        if user.role == User.Role.ADMIN:
            return qs
        if user.role == User.Role.TEACHER:
            return qs.filter(Q(teacher=user) | Q(is_published=True))
        return qs.filter(is_published=True)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        if user.is_authenticated and user.role == User.Role.STUDENT:
            context["enrolled_ids"] = set(
                Enrollment.objects.filter(
                    student=user, status=Enrollment.Status.ACTIVE
                ).values_list("course_id", flat=True)
            )
        return context

    def get_permissions(self):
        if self.action in WRITE_ACTIONS:
            return [IsTeacherOrAdmin(), IsOwnerTeacherOrAdmin()]
        if self.action == "enroll":
            return [IsStudent()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == User.Role.TEACHER:
            serializer.save(teacher=user)
        elif "teacher" not in serializer.validated_data:
            raise ValidationError({"teacher": "Obligatoire pour un administrateur."})
        else:
            serializer.save()

    def perform_update(self, serializer):
        if self.request.user.role == User.Role.TEACHER:
            serializer.save(teacher=serializer.instance.teacher)  # un enseignant ne réassigne pas
        else:
            serializer.save()

    @extend_schema(request=None, responses=EnrollmentSerializer)
    @action(detail=True, methods=["post"])
    def enroll(self, request, pk=None):
        """L'étudiant connecté s'inscrit au cours."""
        course = self.get_object()
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user, course=course
        )
        if not created:
            if enrollment.status == Enrollment.Status.ACTIVE:
                return Response(EnrollmentSerializer(enrollment).data)
            enrollment.status = Enrollment.Status.ACTIVE
            enrollment.save(update_fields=["status", "updated_at"])
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @extend_schema(responses=CourseSerializer(many=True))
    @action(detail=False, methods=["get"], url_path="mine")
    def mine(self, request):
        """Étudiant : cours suivis. Enseignant : cours enseignés."""
        user = request.user
        qs = self.get_queryset()
        if user.role == User.Role.STUDENT:
            qs = qs.filter(
                enrollments__student=user, enrollments__status=Enrollment.Status.ACTIVE
            )
        elif user.role == User.Role.TEACHER:
            qs = qs.filter(teacher=user)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page if page is not None else qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["course", "student", "status"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Enrollment.objects.none()
        user = self.request.user
        qs = Enrollment.objects.select_related("student", "course")
        if user.role == User.Role.ADMIN:
            return qs
        if user.role == User.Role.TEACHER:
            return qs.filter(course__teacher=user)
        return qs.filter(student=user)

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsTeacherOrAdmin(), IsOwnerTeacherOrAdmin()]
        if self.action == "drop":
            return [IsStudent()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == User.Role.STUDENT:
            student = user
        elif user.role == User.Role.ADMIN:
            try:
                student = User.objects.get(
                    pk=self.request.data.get("student"), role=User.Role.STUDENT
                )
            except (User.DoesNotExist, ValueError, TypeError):
                raise ValidationError({"student": "Étudiant introuvable."})
        else:
            raise PermissionDenied("Action non autorisée.")
        course = serializer.validated_data["course"]
        if Enrollment.objects.filter(student=student, course=course).exists():
            raise ValidationError("Cet étudiant est déjà inscrit à ce cours.")
        serializer.save(student=student)

    @extend_schema(request=None, responses=EnrollmentSerializer)
    @action(detail=True, methods=["post"])
    def drop(self, request, pk=None):
        """L'étudiant abandonne le cours."""
        enrollment = self.get_object()
        enrollment.status = Enrollment.Status.DROPPED
        enrollment.save(update_fields=["status", "updated_at"])
        return Response(EnrollmentSerializer(enrollment).data)


class TimetableViewSet(viewsets.ModelViewSet):
    """Emploi du temps (consultation étudiant/enseignant, gestion enseignant/admin)."""

    serializer_class = TimetableSlotSerializer
    filterset_fields = ["course", "weekday"]
    ordering_fields = ["weekday", "start_time"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TimetableSlot.objects.none()
        user = self.request.user
        qs = TimetableSlot.objects.select_related("course")
        if user.role == User.Role.ADMIN:
            return qs
        if user.role == User.Role.TEACHER:
            return qs.filter(course__teacher=user)
        return qs.filter(
            course__enrollments__student=user,
            course__enrollments__status=Enrollment.Status.ACTIVE,
        )

    def get_permissions(self):
        if self.action in WRITE_ACTIONS:
            return [IsTeacherOrAdmin(), IsOwnerTeacherOrAdmin()]
        return [IsAuthenticated()]


class GradeViewSet(viewsets.ModelViewSet):
    """Notes. Lecture : étudiant (les siennes), enseignant (ses cours). Saisie : enseignant/admin."""

    serializer_class = GradeSerializer
    filterset_fields = ["enrollment", "enrollment__course", "enrollment__student"]
    ordering_fields = ["created_at", "score"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Grade.objects.none()
        user = self.request.user
        qs = Grade.objects.select_related("enrollment__course", "enrollment__student")
        if user.role == User.Role.ADMIN:
            return qs
        if user.role == User.Role.TEACHER:
            return qs.filter(enrollment__course__teacher=user)
        return qs.filter(enrollment__student=user)

    def get_permissions(self):
        if self.action in WRITE_ACTIONS or self.action == "bulk":
            return [IsTeacherOrAdmin(), IsOwnerTeacherOrAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(graded_by=self.request.user)

    @extend_schema(request=BulkGradeSerializer, responses=GradeSerializer(many=True))
    @action(detail=False, methods=["post"])
    def bulk(self, request):
        """Saisie en lot : une évaluation, plusieurs étudiants (ré-appel = mise à jour)."""
        serializer = BulkGradeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        course = data["course"]

        enrollments = {
            e.student_id: e
            for e in Enrollment.objects.filter(
                course=course, status=Enrollment.Status.ACTIVE
            )
        }
        missing = [i["student"] for i in data["grades"] if i["student"] not in enrollments]
        if missing:
            raise ValidationError(
                {"grades": f"Étudiants non inscrits à ce cours : {sorted(set(missing))}"}
            )

        saved = []
        with transaction.atomic():
            for item in data["grades"]:
                grade, _ = Grade.objects.update_or_create(
                    enrollment=enrollments[item["student"]],
                    title=data["title"],
                    defaults={
                        "score": item["score"],
                        "max_score": data["max_score"],
                        "coefficient": data["coefficient"],
                        "comment": item.get("comment", ""),
                        "graded_by": request.user,
                    },
                )
                saved.append(grade)
        return Response(
            GradeSerializer(saved, many=True, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class TranscriptView(APIView):
    """Relevé de notes avec moyennes par cours et moyenne générale (/20)."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "student", OpenApiTypes.INT, description="ID étudiant (enseignant/admin uniquement)"
            )
        ],
        responses=OpenApiTypes.OBJECT,
    )
    def get(self, request):
        user = request.user
        if user.role == User.Role.STUDENT:
            return Response(compute_transcript(user))

        student_id = request.query_params.get("student")
        if not student_id:
            raise ValidationError({"student": "Paramètre obligatoire."})
        try:
            student = User.objects.get(pk=student_id, role=User.Role.STUDENT)
        except (User.DoesNotExist, ValueError):
            raise ValidationError({"student": "Étudiant introuvable."})
        teacher = user if user.role == User.Role.TEACHER else None
        return Response(compute_transcript(student, teacher=teacher))
