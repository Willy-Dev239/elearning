"""Règles d'accès aux contenus d'un cours (partagées par mediahub et assessment)."""
from accounts.models import User

from .models import Course, Enrollment


def accessible_course_ids(user):
    """IDs des cours dont l'utilisateur peut consulter le contenu.

    - administrateur : None (= tous les cours)
    - enseignant     : ses propres cours
    - étudiant       : cours où il est inscrit ET (gratuits OU payés via Mobile Money)
    """
    from billing.models import Payment  # import local : évite la dépendance circulaire

    if user.role == User.Role.ADMIN:
        return None
    if user.role == User.Role.TEACHER:
        return set(Course.objects.filter(teacher=user).values_list("id", flat=True))

    enrolled = Course.objects.filter(
        enrollments__student=user, enrollments__status=Enrollment.Status.ACTIVE
    )
    free_ids = set(enrolled.filter(price=0).values_list("id", flat=True))
    paid_course_ids = set(
        Payment.objects.filter(
            student=user, status=Payment.Status.SUCCESS, course__isnull=False
        ).values_list("course_id", flat=True)
    )
    paid_ids = set(enrolled.filter(id__in=paid_course_ids).values_list("id", flat=True))
    return free_ids | paid_ids


def can_access_course(user, course):
    ids = accessible_course_ids(user)
    return ids is None or course.id in ids
