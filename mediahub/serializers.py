import os

from django.conf import settings
from django.urls import reverse
from rest_framework import serializers

from accounts.models import User

from .models import CourseMaterial, MaterialProgress

ALLOWED_EXTENSIONS = {
    CourseMaterial.Kind.VIDEO: {".mp4", ".mkv", ".webm", ".mov", ".m4v"},
    CourseMaterial.Kind.DOCUMENT: {
        ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".txt", ".zip",
    },
    CourseMaterial.Kind.AUDIO: {".mp3", ".m4a", ".wav", ".ogg"},
}


class CourseMaterialSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True, required=False)
    stream_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    last_position_seconds = serializers.SerializerMethodField()

    class Meta:
        model = CourseMaterial
        fields = (
            "id", "course", "title", "description", "kind", "file", "file_size",
            "content_type", "is_free_preview", "position", "uploaded_by",
            "stream_url", "download_url", "completed", "last_position_seconds", "created_at",
        )
        read_only_fields = ("file_size", "content_type", "uploaded_by", "created_at")

    def validate_course(self, course):
        user = self.context["request"].user
        if user.role == User.Role.TEACHER and course.teacher_id != user.id:
            raise serializers.ValidationError("Ce cours ne vous appartient pas.")
        return course

    def validate(self, attrs):
        uploaded = attrs.get("file")
        if self.instance is None and uploaded is None:
            raise serializers.ValidationError({"file": "Fichier obligatoire."})
        if uploaded is not None:
            kind = attrs.get("kind", getattr(self.instance, "kind", None))
            ext = os.path.splitext(uploaded.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS.get(kind, set()):
                raise serializers.ValidationError(
                    {"file": f"Extension {ext or '(aucune)'} non autorisée pour le type '{kind}'."}
                )
            if uploaded.size > settings.MAX_UPLOAD_MB * 1024 * 1024:
                raise serializers.ValidationError(
                    {"file": f"Fichier trop volumineux (max {settings.MAX_UPLOAD_MB} Mo)."}
                )
        return attrs

    def _absolute(self, name, obj):
        url = reverse(name, args=[obj.pk])
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    def get_stream_url(self, obj) -> str:
        return self._absolute("material-stream", obj)

    def get_download_url(self, obj) -> str:
        return self._absolute("material-download", obj)

    def _progress(self, obj):
        cache = self.context.setdefault("_progress_cache", {})
        if "map" not in cache:
            request = self.context.get("request")
            if request and request.user.is_authenticated and request.user.role == User.Role.STUDENT:
                cache["map"] = {
                    p.material_id: p
                    for p in MaterialProgress.objects.filter(student=request.user)
                }
            else:
                cache["map"] = {}
        return cache["map"].get(obj.id)

    def get_completed(self, obj) -> bool:
        progress = self._progress(obj)
        return bool(progress and progress.completed)

    def get_last_position_seconds(self, obj) -> int:
        progress = self._progress(obj)
        return progress.last_position_seconds if progress else 0


class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialProgress
        fields = ("completed", "last_position_seconds")
