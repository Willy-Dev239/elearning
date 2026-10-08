from rest_framework import viewsets

from accounts.permissions import read_or
from .models import Classroom, Enrollment, School
from .serializers import ClassroomSerializer, EnrollmentSerializer, SchoolSerializer

ReadOnlyOrAdmin = read_or("ADMIN")


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [ReadOnlyOrAdmin]


class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.select_related("school")
    serializer_class = ClassroomSerializer
    permission_classes = [ReadOnlyOrAdmin]


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [ReadOnlyOrAdmin]

    def get_queryset(self):
        u = self.request.user
        qs = Enrollment.objects.select_related("student", "classroom__school")
        if u.role == "ADMIN":
            return qs
        if u.role == "TEACHER":
            return qs.filter(classroom__courses__teacher=u).distinct()
        return qs.filter(student=u)
