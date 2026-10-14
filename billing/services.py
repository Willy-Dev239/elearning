from django.db import transaction
from django.utils import timezone

from .models import Payment


def mark_payment(payment, status, transaction_id=""):
    """Change le statut d'un paiement (idempotent : un paiement réussi reste réussi)."""
    with transaction.atomic():
        locked = Payment.objects.select_for_update().get(pk=payment.pk)
        if locked.status == Payment.Status.SUCCESS:
            return locked
        locked.status = status
        if transaction_id:
            locked.provider_transaction_id = transaction_id
        if status == Payment.Status.SUCCESS:
            locked.paid_at = timezone.now()
        locked.save()
    return locked
