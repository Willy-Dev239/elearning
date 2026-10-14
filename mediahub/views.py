import mimetypes
import os

from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from academic.access import accessible_course_ids
from academic.models import Course, Enrollment
from accounts.models import User
from core.permissions import IsOwnerTeacherOrAdmin, IsStudent, IsTeacherOrAdmin

from .models import CourseMaterial, MaterialProgress
from .serializers import CourseMaterialSerializer, ProgressSerializer
from .streaming import range_file_response

WRITE_ACTIONS = ("create", "update", "partial_update", "destroy")


class MaterialViewSet(viewsets.ModelViewSet):
    """Supports de cours (vidéos / documents) + streaming protégé."""

    serializer_class = CourseMaterialSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ["course", "kind"]
    search_fields = ["title", "description"]
    ordering_fields = ["position", "created_at", "title"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return CourseMaterial.objects.none()
        user = self.request.user
        qs = CourseMaterial.objects.select_related("course")
        if user.role == User.Role.ADMIN:
            return qs
        if user.role == User.Role.TEACHER:
            return qs.filter(course__teacher=user)
        ids = accessible_course_ids(user)
        return qs.filter(
            Q(course_id__in=ids) | Q(is_free_preview=True, course__is_published=True)
        )

    def get_permissions(self):
        if self.action in WRITE_ACTIONS:
            return [IsTeacherOrAdmin(), IsOwnerTeacherOrAdmin()]
        if self.action == "progress":
            return [IsStudent()]
        return [IsAuthenticated()]

    def _save_file_meta(self, serializer, **extra):
        uploaded = serializer.validated_data.get("file")
        if uploaded is not None:
            extra["file_size"] = uploaded.size
            extra["content_type"] = (
                getattr(uploaded, "content_type", "")
                or mimetypes.guess_type(uploaded.name)[0]
                or ""
            )
        serializer.save(**extra)

    def perform_create(self, serializer):
        self._save_file_meta(serializer, uploaded_by=self.request.user)

    def perform_update(self, serializer):
        self._save_file_meta(serializer)

    def perform_destroy(self, instance):
        instance.file.delete(save=False)
        instance.delete()

    def _serve(self, request, as_attachment):
        material = self.get_object()
        if not material.file:
            raise NotFound("Fichier introuvable.")
        filename = f"{material.title}{os.path.splitext(material.file.name)[1]}".replace('"', "")
        content_type = (
            material.content_type or mimetypes.guess_type(material.file.name)[0]
        )
        return range_file_response(request, material.file, content_type, filename, as_attachment)

    @extend_schema(responses={(200, "application/octet-stream"): OpenApiTypes.BINARY})
    @action(detail=True, methods=["get"])
    def stream(self, request, pk=None):
        """Streaming progressif (en-tête `Range` supporté → 206 Partial Content)."""
        return self._serve(request, as_attachment=False)

    @extend_schema(responses={(200, "application/octet-stream"): OpenApiTypes.BINARY})
    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """Téléchargement du fichier."""
        return self._serve(request, as_attachment=True)

    @extend_schema(request=ProgressSerializer, responses=ProgressSerializer)
    @action(detail=True, methods=["post"])
    def progress(self, request, pk=None):
        """L'étudiant enregistre sa progression (terminé, position de lecture en secondes)."""
        material = self.get_object()
        serializer = ProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj, _ = MaterialProgress.objects.update_or_create(
            student=request.user, material=material, defaults=serializer.validated_data
        )
        return Response(ProgressSerializer(obj).data)


class CourseProgressView(APIView):
    """Avancement de l'étudiant dans un cours (suivi des cours)."""

    permission_classes = [IsStudent]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request, course_id):
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            raise NotFound("Cours introuvable.")
        if not Enrollment.objects.filter(
            student=request.user, course=course, status=Enrollment.Status.ACTIVE
        ).exists():
            raise NotFound("Vous n'êtes pas inscrit à ce cours.")

        materials = list(course.materials.all())
        done = set(
            MaterialProgress.objects.filter(
                student=request.user, material__course=course, completed=True
            ).values_list("material_id", flat=True)
        )
        total = len(materials)
        return Response(
            {
                "course": course.id,
                "total": total,
                "completed": len(done),
                "percent": round(len(done) / total * 100, 1) if total else 0,
                "items": [
                    {"material": m.id, "title": m.title, "kind": m.kind, "completed": m.id in done}
                    for m in materials
                ],
            }
        )
