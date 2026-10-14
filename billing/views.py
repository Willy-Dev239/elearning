import hashlib
import hmac
from datetime import date

from django.conf import settings
from django.db.models import Sum
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from academic.models import Enrollment
from accounts.models import User
from core.permissions import IsAdmin, IsStudent, IsTeacherOrAdmin

from .gateways import get_gateway
from .models import FeeStructure, Installment, Payment
from .serializers import (
    FeeStructureSerializer,
    InstallmentSerializer,
    PaymentSerializer,
    WebhookSerializer,
)
from .services import mark_payment

WRITE_ACTIONS = ("create", "update", "partial_update", "destroy")


class FeeStructureViewSet(viewsets.ModelViewSet):
    """Frais de scolarité (lecture : tous ; écriture : administrateur)."""

    queryset = FeeStructure.objects.prefetch_related("installments")
    serializer_class = FeeStructureSerializer
    filterset_fields = ["academic_year", "is_active"]

    def get_permissions(self):
        return [IsAdmin()] if self.action in WRITE_ACTIONS else [IsAuthenticated()]


class InstallmentViewSet(viewsets.ModelViewSet):
    queryset = Installment.objects.select_related("fee")
    serializer_class = InstallmentSerializer
    filterset_fields = ["fee"]

    def get_permissions(self):
        return [IsAdmin()] if self.action in WRITE_ACTIONS else [IsAuthenticated()]


class PaymentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Paiements Mobile Money (tranches de scolarité ou modules payants)."""

    serializer_class = PaymentSerializer
    filterset_fields = ["status", "provider", "course", "installment"]
    ordering_fields = ["created_at", "amount"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Payment.objects.none()
        user = self.request.user
        qs = Payment.objects.select_related("student", "installment", "course")
        if user.role == User.Role.ADMIN:
            return qs
        if user.role == User.Role.TEACHER:
            return qs.filter(
                student__enrollments__course__teacher=user
            ).distinct()
        return qs.filter(student=user)

    def get_permissions(self):
        if self.action == "create":
            return [IsStudent()]
        if self.action == "confirm":
            return [IsAdmin()]
        return [IsAuthenticated()]

    @extend_schema(request=PaymentSerializer, responses=PaymentSerializer)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(student=request.user)
        result = get_gateway().initiate(payment)
        payment.refresh_from_db()
        data = self.get_serializer(payment).data
        data["message"] = result.get("message", "")
        return Response(data, status=status.HTTP_201_CREATED)

    @extend_schema(request=None, responses=PaymentSerializer)
    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        """Confirmation manuelle par l'administrateur (ex. paiement au guichet)."""
        payment = mark_payment(self.get_object(), Payment.Status.SUCCESS, "MANUAL")
        return Response(self.get_serializer(payment).data)


class WebhookView(APIView):
    """Callback de l'opérateur Mobile Money.

    Signature : en-tête `X-Signature` = HMAC-SHA256 (hex) du corps brut avec
    MOBILE_MONEY_WEBHOOK_SECRET.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(request=WebhookSerializer, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        raw_body = request.body  # à lire AVANT request.data
        expected = hmac.new(
            settings.MOBILE_MONEY_WEBHOOK_SECRET.encode(), raw_body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(request.headers.get("X-Signature", ""), expected):
            return Response({"detail": "Signature invalide."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = WebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            payment = Payment.objects.get(reference=data["reference"])
        except Payment.DoesNotExist:
            return Response({"detail": "Paiement introuvable."}, status=status.HTTP_404_NOT_FOUND)
        payment = mark_payment(payment, data["status"], data["transaction_id"])
        return Response({"reference": payment.reference, "status": payment.status})


def _installment_status(installment, payments_by_installment):
    payments = payments_by_installment.get(installment.id, [])
    if any(p.status == Payment.Status.SUCCESS for p in payments):
        return "paid"
    if any(p.status == Payment.Status.PENDING for p in payments):
        return "pending"
    return "overdue" if installment.due_date < date.today() else "unpaid"


class MyAccountView(APIView):
    """Situation financière de l'étudiant : tranches, modules payants, solde."""

    permission_classes = [IsStudent]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        user = request.user
        payments = list(Payment.objects.filter(student=user))
        by_installment, by_course = {}, {}
        for p in payments:
            if p.installment_id:
                by_installment.setdefault(p.installment_id, []).append(p)
            else:
                by_course.setdefault(p.course_id, []).append(p)

        total_due, total_paid = 0, 0
        tuition = []
        for fee in FeeStructure.objects.filter(is_active=True).prefetch_related("installments"):
            rows = []
            for inst in fee.installments.all():
                state = _installment_status(inst, by_installment)
                total_due += inst.amount
                if state == "paid":
                    total_paid += inst.amount
                rows.append(
                    {
                        "id": inst.id, "label": inst.label, "amount": str(inst.amount),
                        "due_date": inst.due_date, "status": state,
                    }
                )
            tuition.append({"fee_id": fee.id, "title": fee.title, "installments": rows})

        modules = []
        enrollments = Enrollment.objects.filter(
            student=user, status=Enrollment.Status.ACTIVE, course__price__gt=0
        ).select_related("course")
        for enrollment in enrollments:
            course = enrollment.course
            payments_for_course = by_course.get(course.id, [])
            paid = any(p.status == Payment.Status.SUCCESS for p in payments_for_course)
            pending = any(p.status == Payment.Status.PENDING for p in payments_for_course)
            total_due += course.price
            if paid:
                total_paid += course.price
            modules.append(
                {
                    "course_id": course.id, "code": course.code, "title": course.title,
                    "price": str(course.price),
                    "status": "paid" if paid else "pending" if pending else "unpaid",
                }
            )

        return Response(
            {
                "currency": settings.CURRENCY,
                "tuition": tuition,
                "modules": modules,
                "total_due": str(total_due),
                "total_paid": str(total_paid),
                "balance": str(total_due - total_paid),
            }
        )


class TrackingView(APIView):
    """Suivi du règlement des frais des étudiants (enseignant : ses étudiants ; admin : tous)."""

    permission_classes = [IsTeacherOrAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter("course", OpenApiTypes.INT, description="Filtrer par cours"),
            OpenApiParameter("status", OpenApiTypes.STR, description="paid | partial | unpaid"),
        ],
        responses=OpenApiTypes.OBJECT,
    )
    def get(self, request):
        user = request.user
        enrollments = Enrollment.objects.filter(
            status=Enrollment.Status.ACTIVE
        ).select_related("student", "course")
        if user.role == User.Role.TEACHER:
            enrollments = enrollments.filter(course__teacher=user)
        course_id = request.query_params.get("course")
        if course_id:
            enrollments = enrollments.filter(course_id=course_id)

        tuition_total = (
            Installment.objects.filter(fee__is_active=True).aggregate(s=Sum("amount"))["s"] or 0
        )

        students, paid_courses = {}, {}
        for e in enrollments:
            students[e.student_id] = e.student
            if e.course.price > 0:
                paid_courses.setdefault(e.student_id, {})[e.course_id] = e.course.price

        payments = Payment.objects.filter(
            student_id__in=students.keys(), status=Payment.Status.SUCCESS
        )
        paid_tuition, paid_modules = {}, {}
        for p in payments:
            if p.installment_id:
                paid_tuition[p.student_id] = paid_tuition.get(p.student_id, 0) + p.amount
            elif p.course_id in paid_courses.get(p.student_id, {}):
                paid_modules[p.student_id] = paid_modules.get(p.student_id, 0) + p.amount

        results = []
        wanted = request.query_params.get("status")
        for sid, student in students.items():
            due = tuition_total + sum(paid_courses.get(sid, {}).values())
            paid = paid_tuition.get(sid, 0) + paid_modules.get(sid, 0)
            balance = due - paid
            state = "paid" if balance <= 0 else "partial" if paid > 0 else "unpaid"
            if wanted and wanted != state:
                continue
            results.append(
                {
                    "student": {"id": sid, "name": student.get_full_name() or student.username},
                    "total_due": str(due), "total_paid": str(paid),
                    "balance": str(balance), "status": state,
                }
            )
        results.sort(key=lambda r: float(r["balance"]), reverse=True)
        return Response({"currency": settings.CURRENCY, "count": len(results), "results": results})
