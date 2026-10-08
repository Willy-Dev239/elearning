from rest_framework_simplejwt.authentication import JWTAuthentication


class QueryTokenJWTAuthentication(JWTAuthentication):
    """Accepte ?token=<jwt> (pour <video src> / liens de documents)."""
    def authenticate(self, request):
        raw = request.query_params.get("token")
        if raw:
            token = self.get_validated_token(raw.encode())
            return self.get_user(token), token
        return super().authenticate(request)
