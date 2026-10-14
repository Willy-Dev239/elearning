from rest_framework.exceptions import NotAcceptable
from rest_framework.negotiation import DefaultContentNegotiation


class LenientContentNegotiation(DefaultContentNegotiation):
    """Ne rejette jamais une requête à cause de l'en-tête Accept.

    Utile pour les lecteurs vidéo mobiles qui envoient des Accept exotiques
    (ex. video/mp4) sur les endpoints de streaming.
    """

    def select_renderer(self, request, renderers, format_suffix=None):
        try:
            return super().select_renderer(request, renderers, format_suffix)
        except NotAcceptable:
            return renderers[0], renderers[0].media_type
