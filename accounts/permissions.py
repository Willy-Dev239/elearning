from rest_framework.permissions import SAFE_METHODS, BasePermission


def role_perm(*roles):
    """Accès réservé aux rôles donnés."""
    class P(BasePermission):
        def has_permission(self, request, view):
            u = request.user
            return bool(u and u.is_authenticated and u.role in roles)
    return P


def read_or(*roles):
    """Lecture pour tout utilisateur connecté, écriture pour les rôles donnés."""
    class P(BasePermission):
        def has_permission(self, request, view):
            u = request.user
            if not (u and u.is_authenticated):
                return False
            return request.method in SAFE_METHODS or u.role in roles
    return P


IsAdminRole = role_perm("ADMIN")
IsStudent = role_perm("STUDENT")
