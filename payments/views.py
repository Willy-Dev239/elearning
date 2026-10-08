from django.db.models import Count, Sum
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.permissions import IsAdminRole, IsStudent, read_or
from courses.models import Course, Lesson
from quizzes.models import Quiz
from schools.models import Classroom
from . import gateway
from .models import Fee, Payment
from .serializers import FeeSerializer, PaymentSerializer


class FeeViewSet(viewsets.ModelViewSet):
    serializer_class = FeeSerializer
    permission_classes = [read_or("ADMIN")]

    def get_queryset(self):
        u = self.request.user
        qs = Fee.objects.select_related("classroom__school")
        if u.role == "ADMIN":
            return qs
        if u.role == "STUDENT":
            return qs.filter(classroom__enrollments__student=u).distinct()
        return qs.none()


class PaymentViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = PaymentSerializer

    def get_permissions(self):
        return [IsStudent()] if self.action == "create" else [IsAuthenticated()]

    def get_queryset(self):
        u = self.request.user
        qs = Payment.objects.select_related("fee", "student")
        if u.role == "ADMIN":
            return qs
        return qs.filter(student=u) if u.role == "STUDENT" else qs.none()

    def perform_create(self, serializer):
        d = serializer.validated_data
        ok, ref = gateway.charge(method=d["method"], phone=d.get("phone", ""), amount=d["amount"])
        serializer.save(student=self.request.user, reference=ref,
                        status=Payment.Status.PAID if ok else Payment.Status.FAILED)

    @action(detail=True, methods=["get"])
    def receipt(self, request, pk=None):
        p = self.get_object()
        return Response({
            "reference": p.reference, "status": p.status, "date": p.created,
            "student": p.student.get_full_name() or p.student.username,
            "fee": p.fee.title, "classroom": str(p.fee.classroom),
            "amount": p.amount, "method": p.get_method_display(),
        })


class StatsView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        paid = Payment.objects.filter(status="PAID").aggregate(s=Sum("amount"), n=Count("id"))
        return Response({
            "students": User.objects.filter(role="STUDENT").count(),
            "teachers": User.objects.filter(role="TEACHER").count(),
            "classrooms": Classroom.objects.count(),
            "courses": Course.objects.count(),
            "lessons": Lesson.objects.count(),
            "quizzes": Quiz.objects.count(),
            "payments": paid["n"],
            "total_paid": paid["s"] or 0,
        })
