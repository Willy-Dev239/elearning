from rest_framework import viewsets
from rest_framework.decorators import action

from accounts.auth import QueryTokenJWTAuthentication
from accounts.permissions import read_or
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .streaming import stream_file

TeacherWrite = read_or("TEACHER", "ADMIN")


def visible_courses(user):
    """Cours accessibles : admin = tous, enseignant = les siens, étudiant = ceux de ses classes."""
    if user.role == "ADMIN":
        return Course.objects.all()
    if user.role == "TEACHER":
        return Course.objects.filter(teacher=user)
    return Course.objects.filter(classroom__enrollments__student=user).distinct()


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [TeacherWrite]

    def get_queryset(self):
        return visible_courses(self.request.user).select_related("teacher", "classroom__school")

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [TeacherWrite]

    def get_queryset(self):
        qs = Lesson.objects.filter(course__in=visible_courses(self.request.user))
        course = self.request.query_params.get("course")
        return qs.filter(course_id=course) if course else qs

    @action(detail=True, methods=["get"], authentication_classes=[QueryTokenJWTAuthentication])
    def stream(self, request, pk=None):
        """Streaming vidéo/document (Range supporté). Auth : header Bearer ou ?token=."""
        return stream_file(request, self.get_object().file.path)
