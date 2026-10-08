from rest_framework import serializers
from .models import Classroom, Enrollment, School


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["id", "name", "address"]


class ClassroomSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = Classroom
        fields = ["id", "school", "school_name", "name"]


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    classroom_name = serializers.CharField(source="classroom.__str__", read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "student", "student_name", "classroom", "classroom_name", "academic_year"]

    def validate_student(self, u):
        if u.role != "STUDENT":
            raise serializers.ValidationError("L'utilisateur doit être un étudiant.")
        return u
