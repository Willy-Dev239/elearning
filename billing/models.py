import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q

from core.models import TimeStampedModel


class FeeStructure(TimeStampedModel):
    """Frais de scolarité d'une année, découpés en tranches (Installment)."""

    title = models.CharField(max_length=150)
    academic_year = models.ForeignKey(
        "academic.AcademicYear", on_delete=models.PROTECT, related_name="fees", null=True, blank=True
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Installment(TimeStampedModel):
    fee = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name="installments")
    label = models.CharField(max_length=100, help_text="ex. Tranche 1")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["fee", "order", "due_date"]

    def __str__(self):
        return f"{self.fee.title} — {self.label}"


def generate_reference():
    return f"PAY-{uuid.uuid4().hex[:16].upper()}"


class Payment(TimeStampedModel):
    class Provider(models.TextChoices):
        LUMICASH = "lumicash", "Lumicash"
        ECOCASH = "ecocash", "EcoCash"
        OTHER = "other", "Autre"

    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        SUCCESS = "success", "Payé"
        FAILED = "failed", "Échoué"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    # Exactement UNE cible : une tranche de scolarité OU un module payant
    installment = models.ForeignKey(
        Installment, on_delete=models.PROTECT, null=True, blank=True, related_name="payments"
    )
    course = models.ForeignKey(
        "academic.Course", on_delete=models.PROTECT, null=True, blank=True, related_name="payments"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    provider = models.CharField(max_length=20, choices=Provider.choices)
    phone_number = models.CharField(max_length=20)
    reference = models.CharField(max_length=40, unique=True, default=generate_reference)
    provider_transaction_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(installment__isnull=False, course__isnull=True)
                    | Q(installment__isnull=True, course__isnull=False)
                ),
                name="payment_exactly_one_target",
            )
        ]

    def __str__(self):
        return f"{self.reference} ({self.status})"
