from rest_framework import serializers
from .models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)
    classroom_name = serializers.CharField(source="classroom.__str__", read_only=True)

    class Meta:
        model = Course
        fields = ["id", "classroom", "classroom_name", "teacher", "teacher_name", "title", "description"]
        read_only_fields = ["teacher"]


class LessonSerializer(serializers.ModelSerializer):
    stream_url = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ["id", "course", "title", "kind", "file", "order", "stream_url"]
        extra_kwargs = {"file": {"write_only": True}}

    def get_stream_url(self, obj):
        return f"/api/lessons/{obj.id}/stream/"

    def validate_course(self, course):
        u = self.context["request"].user
        if u.role != "ADMIN" and course.teacher_id != u.id:
            raise serializers.ValidationError("Ce cours ne vous appartient pas.")
        return course
