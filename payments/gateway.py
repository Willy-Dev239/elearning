import uuid


def charge(*, method, phone, amount):
    """SIMULATION d'une passerelle de paiement. Retourne (succès, référence).

    À remplacer par l'intégration réelle (Mobile Money, banque...) :
    appeler l'API du fournisseur ici et retourner sa référence de transaction.
    """
    ref = uuid.uuid4().hex[:10].upper()
    if method == "MOBILE_MONEY" and not phone:
        return False, f"FAIL-{ref}"
    return True, f"PAY-{ref}"
