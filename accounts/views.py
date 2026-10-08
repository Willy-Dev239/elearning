from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny

from .models import User
from .permissions import IsAdminRole
from .serializers import RegisterSerializer, UserAdminSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """Inscription libre : crée un compte ÉTUDIANT."""
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    """Gestion des utilisateurs (back office uniquement)."""
    queryset = User.objects.order_by("id")
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminRole]
