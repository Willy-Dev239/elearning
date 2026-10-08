from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "phone", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "email", "phone"]

    def create(self, vd):
        return User.objects.create_user(**vd, role=User.Role.STUDENT)


class UserAdminSerializer(RegisterSerializer):
    class Meta(RegisterSerializer.Meta):
        fields = RegisterSerializer.Meta.fields + ["id", "role"]

    def create(self, vd):
        role = vd.pop("role", User.Role.STUDENT)
        return User.objects.create_user(**vd, role=role)
