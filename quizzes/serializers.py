from rest_framework import serializers
from .models import Attempt, Choice, Question, Quiz


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text", "is_correct"]

    def to_representation(self, inst):
        data = super().to_representation(inst)
        req = self.context.get("request")
        if req and req.user.role == "STUDENT":
            data.pop("is_correct")  # l'étudiant ne voit pas les bonnes réponses
        return data


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "text", "choices"]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Quiz
        fields = ["id", "course", "title", "description", "pass_mark", "questions"]

    def validate_course(self, course):
        u = self.context["request"].user
        if u.role != "ADMIN" and course.teacher_id != u.id:
            raise serializers.ValidationError("Ce cours ne vous appartient pas.")
        return course

    def validate_questions(self, qs):
        for q in qs:
            if len(q["choices"]) < 2 or not any(c.get("is_correct") for c in q["choices"]):
                raise serializers.ValidationError("Chaque question : 2 choix minimum dont 1 correct (*).")
        return qs

    def create(self, vd):
        questions = vd.pop("questions", [])
        quiz = Quiz.objects.create(**vd)
        for i, q in enumerate(questions):
            choices = q.pop("choices")
            question = Question.objects.create(quiz=quiz, order=i, **q)
            Choice.objects.bulk_create([Choice(question=question, **c) for c in choices])
        return quiz


class AttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    percent = serializers.IntegerField(read_only=True)
    passed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Attempt
        fields = ["id", "quiz", "quiz_title", "student_name", "score", "total", "percent", "passed", "created"]
