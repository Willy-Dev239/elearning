from rest_framework import serializers

from accounts.models import User

from .models import AcademicYear, Course, Enrollment, Grade, SchoolClass, TimetableSlot

class SchoolClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClass
        fields = ("id", "name", "academic_year")
class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ("id", "name", "start_date", "end_date", "is_current")


class CourseSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.TEACHER), required=False
    )
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    enrolled_count = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id", "code", "title", "description", "teacher", "teacher_name",
            "academic_year", "credits", "price", "is_paid", "is_published",
            "enrolled_count", "is_enrolled", "created_at",
        )
        read_only_fields = ("created_at",)

    def get_enrolled_count(self, obj) -> int:
        count = getattr(obj, "active_enrollments", None)
        if count is None:
            count = obj.enrollments.filter(status=Enrollment.Status.ACTIVE).count()
        return count

    def get_is_enrolled(self, obj) -> bool:
        ids = self.context.get("enrolled_ids")
        if ids is not None:
            return obj.id in ids
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.role == User.Role.STUDENT:
            return Enrollment.objects.filter(
                student=request.user, course=obj, status=Enrollment.Status.ACTIVE
            ).exists()
        return False


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)
    course_code = serializers.CharField(source="course.code", read_only=True)

    class Meta:
        model = Enrollment
        fields = (
            "id", "student", "student_name", "course", "course_code",
            "course_title", "status", "enrolled_at",
        )
        read_only_fields = ("student", "enrolled_at")


class TimetableSlotSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    course_code = serializers.CharField(source="course.code", read_only=True)
    weekday_display = serializers.CharField(source="get_weekday_display", read_only=True)

    class Meta:
        model = TimetableSlot
        fields = (
            "id", "course", "course_code", "course_title", "weekday",
            "weekday_display", "start_time", "end_time", "room",
        )

    def validate_course(self, course):
        user = self.context["request"].user
        if user.role == User.Role.TEACHER and course.teacher_id != user.id:
            raise serializers.ValidationError("Ce cours ne vous appartient pas.")
        return course

    def validate(self, attrs):
        start = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end = attrs.get("end_time", getattr(self.instance, "end_time", None))
        if start and end and start >= end:
            raise serializers.ValidationError("L'heure de fin doit être après l'heure de début.")
        return attrs


class GradeSerializer(serializers.ModelSerializer):
    course = serializers.IntegerField(source="enrollment.course_id", read_only=True)
    course_title = serializers.CharField(source="enrollment.course.title", read_only=True)
    student = serializers.IntegerField(source="enrollment.student_id", read_only=True)
    student_name = serializers.CharField(source="enrollment.student.get_full_name", read_only=True)
    score_on_20 = serializers.FloatField(read_only=True)

    class Meta:
        model = Grade
        fields = (
            "id", "enrollment", "course", "course_title", "student", "student_name",
            "title", "score", "max_score", "coefficient", "comment", "score_on_20",
            "graded_by", "created_at",
        )
        read_only_fields = ("graded_by", "created_at")

    def validate(self, attrs):
        user = self.context["request"].user
        enrollment = attrs.get("enrollment", getattr(self.instance, "enrollment", None))
        if user.role == User.Role.TEACHER and enrollment.course.teacher_id != user.id:
            raise serializers.ValidationError("Cet étudiant n'est pas inscrit à l'un de vos cours.")
        score = attrs.get("score", getattr(self.instance, "score", None))
        max_score = attrs.get("max_score", getattr(self.instance, "max_score", None))
        if score is not None and max_score is not None and score > max_score:
            raise serializers.ValidationError("La note ne peut pas dépasser la note maximale.")
        return attrs


class BulkGradeItemSerializer(serializers.Serializer):
    student = serializers.IntegerField()
    score = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=0)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=255)


class BulkGradeSerializer(serializers.Serializer):
    """Saisie des notes d'une évaluation pour toute une classe."""

    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    title = serializers.CharField(max_length=120)
    max_score = serializers.DecimalField(max_digits=6, decimal_places=2, default=20, min_value=1)
    coefficient = serializers.DecimalField(max_digits=4, decimal_places=2, default=1, min_value=0)
    grades = BulkGradeItemSerializer(many=True, allow_empty=False)

    def validate_course(self, course):
        user = self.context["request"].user
        if user.role == User.Role.TEACHER and course.teacher_id != user.id:
            raise serializers.ValidationError("Ce cours ne vous appartient pas.")
        return course

    def validate(self, attrs):
        for item in attrs["grades"]:
            if item["score"] > attrs["max_score"]:
                raise serializers.ValidationError(
                    f"Note {item['score']} > note maximale ({attrs['max_score']}) pour l'étudiant {item['student']}."
                )
        return attrs
