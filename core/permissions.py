from rest_framework.permissions import BasePermission

from accounts.models import User


class RolePermission(BasePermission):
    roles = ()

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role in self.roles)


class IsAdmin(RolePermission):
    roles = (User.Role.ADMIN,)


class IsTeacher(RolePermission):
    roles = (User.Role.TEACHER,)


class IsStudent(RolePermission):
    roles = (User.Role.STUDENT,)


class IsTeacherOrAdmin(RolePermission):
    roles = (User.Role.TEACHER, User.Role.ADMIN)


def resolve_teacher_id(obj):
    """Retrouve l'enseignant propriétaire d'un objet (cours, quiz, séance...)."""
    for path in (
        "teacher_id",
        "course.teacher_id",
        "quiz.course.teacher_id",
        "enrollment.course.teacher_id",
    ):
        current = obj
        try:
            for part in path.split("."):
                current = getattr(current, part)
            return current
        except AttributeError:
            continue
    return None


class IsOwnerTeacherOrAdmin(BasePermission):
    """Objet modifiable par l'administrateur ou l'enseignant du cours concerné."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == User.Role.ADMIN:
            return True
        return user.role == User.Role.TEACHER and resolve_teacher_id(obj) == user.id
