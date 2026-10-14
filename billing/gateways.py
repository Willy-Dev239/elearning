"""Passerelle Mobile Money.

`SimulatedGateway` permet de tester tout le parcours sans opérateur réel.
Pour brancher un vrai opérateur (Lumicash, EcoCash...), créer une classe avec
la méthode `initiate(payment)` et l'enregistrer dans GATEWAYS ; l'opérateur
confirmera ensuite le paiement via le webhook /api/v1/billing/webhook/.
"""
from django.conf import settings

from .models import Payment
from .services import mark_payment


class BaseGateway:
    def initiate(self, payment):
        raise NotImplementedError


class SimulatedGateway(BaseGateway):
    def initiate(self, payment):
        if settings.MOBILE_MONEY_AUTO_CONFIRM:
            mark_payment(payment, Payment.Status.SUCCESS, f"SIM-{payment.reference[-8:]}")
            return {"message": "Paiement simulé confirmé."}
        return {
            "message": (
                f"Validez le paiement de {payment.amount} {settings.CURRENCY} "
                f"sur le {payment.phone_number} ({payment.get_provider_display()})."
            )
        }


GATEWAYS = {"simulated": SimulatedGateway}


def get_gateway():
    return GATEWAYS[settings.MOBILE_MONEY_GATEWAY]()
