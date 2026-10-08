from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum


class Fee(models.Model):
    classroom = models.ForeignKey("schools.Classroom", on_delete=models.CASCADE, related_name="fees", verbose_name="Classe")
    title = models.CharField("Intitulé", max_length=200)
    amount = models.DecimalField("Montant", max_digits=12, decimal_places=2)
    due_date = models.DateField("Date limite")

    class Meta:
        verbose_name = "frais de scolarité"
        verbose_name_plural = "frais de scolarité"

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

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments", verbose_name="Étudiant")
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name="payments", verbose_name="Frais")
    amount = models.DecimalField("Montant", max_digits=12, decimal_places=2)
    method = models.CharField("Moyen de paiement", max_length=15, choices=Method.choices, default=Method.MOBILE_MONEY)
    phone = models.CharField("Téléphone", max_length=20, blank=True)
    status = models.CharField("Statut", max_length=10, choices=Status.choices, default=Status.PAID)
    reference = models.CharField("Référence", max_length=40, unique=True)
    created = models.DateTimeField("Date", auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "paiement"
        verbose_name_plural = "paiements"

    def __str__(self):
        return self.reference
