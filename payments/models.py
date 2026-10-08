from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum


class Fee(models.Model):
    classroom = models.ForeignKey("schools.Classroom", on_delete=models.CASCADE, related_name="fees")
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.classroom})"

    def paid_by(self, user):
        total = self.payments.filter(student=user, status=Payment.Status.PAID).aggregate(s=Sum("amount"))["s"]
        return total or Decimal("0")

    def remaining_for(self, user):
        return self.amount - self.paid_by(user)


class Payment(models.Model):
    class Method(models.TextChoices):
        MOBILE_MONEY = "MOBILE_MONEY", "Mobile Money"
        CARD = "CARD", "Carte bancaire"
        CASH = "CASH", "Espèces / Banque"

    class Status(models.TextChoices):
        PAID = "PAID", "Payé"
        FAILED = "FAILED", "Échoué"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=15, choices=Method.choices, default=Method.MOBILE_MONEY)
    phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PAID)
    reference = models.CharField(max_length=40, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.reference
