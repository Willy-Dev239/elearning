from django.db import transaction
from rest_framework import serializers

from accounts.models import User

from .models import Answer, Attempt, Choice, Question, Quiz


# ---------- Questions ----------
class ChoiceSerializer(serializers.ModelSerializer):
    """Version enseignant (révèle la bonne réponse)."""

    class Meta:
        model = Choice
        fields = ("id", "text", "is_correct")


class ChoiceStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("id", "text")


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ("id", "quiz", "text", "type", "points", "position", "choices")

    def validate_quiz(self, quiz):
        user = self.context["request"].user
        if user.role == User.Role.TEACHER and quiz.course.teacher_id != user.id:
            raise serializers.ValidationError("Ce quiz ne vous appartient pas.")
        return quiz

    def validate(self, attrs):
        qtype = attrs.get("type", getattr(self.instance, "type", Question.Type.SINGLE))
        choices = attrs.get("choices")
        if qtype == Question.Type.TEXT:
            if choices:
                raise serializers.ValidationError({"choices": "Une question libre n'a pas de choix."})
            return attrs
        if choices is None:
            if self.instance is None:
                raise serializers.ValidationError({"choices": "Les choix sont obligatoires."})
            return attrs
        if len(choices) < 2:
            raise serializers.ValidationError({"choices": "Au moins 2 choix."})
        correct = sum(1 for c in choices if c.get("is_correct"))
        if qtype in (Question.Type.SINGLE, Question.Type.TRUE_FALSE) and correct != 1:
            raise serializers.ValidationError({"choices": "Une seule bonne réponse attendue."})
        if qtype == Question.Type.MULTIPLE and correct < 1:
            raise serializers.ValidationError({"choices": "Au moins une bonne réponse attendue."})
        return attrs

    def create(self, validated_data):
        choices = validated_data.pop("choices", [])
        with transaction.atomic():
            question = Question.objects.create(**validated_data)
            Choice.objects.bulk_create([Choice(question=question, **c) for c in choices])
        return question

    def update(self, instance, validated_data):
        choices = validated_data.pop("choices", None)
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if choices is not None:
                instance.choices.all().delete()
                Choice.objects.bulk_create([Choice(question=instance, **c) for c in choices])
        return instance


class QuestionStudentSerializer(serializers.ModelSerializer):
    choices = ChoiceStudentSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "text", "type", "points", "position", "choices")


# ---------- Quiz ----------
class QuizSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    total_points = serializers.FloatField(read_only=True)
    question_count = serializers.SerializerMethodField()
    attempts_used = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = (
            "id", "course", "course_title", "title", "description", "kind",
            "duration_minutes", "max_attempts", "available_from", "due_date",
            "is_published", "show_corrections", "counts_for_grade", "coefficient",
            "total_points", "question_count", "attempts_used", "created_at",
        )
        read_only_fields = ("created_at",)

    def validate_course(self, course):
        user = self.context["request"].user
        if user.role == User.Role.TEACHER and course.teacher_id != user.id:
            raise serializers.ValidationError("Ce cours ne vous appartient pas.")
        return course

    def get_question_count(self, obj) -> int:
        return obj.questions.count()

    def get_attempts_used(self, obj) -> int:
        request = self.context.get("request")
        if request and request.user.role == User.Role.STUDENT:
            return obj.attempts.filter(student=request.user).count()
        return 0


class QuizDetailSerializer(QuizSerializer):
    questions = serializers.SerializerMethodField()

    class Meta(QuizSerializer.Meta):
        fields = QuizSerializer.Meta.fields + ("questions",)

    def get_questions(self, obj) -> list:
        qs = obj.questions.prefetch_related("choices")
        if self.context["request"].user.role == User.Role.STUDENT:
            return QuestionStudentSerializer(qs, many=True).data
        return QuestionSerializer(qs, many=True, context=self.context).data


# ---------- Tentatives ----------
class AnswerResultSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source="question.text", read_only=True)
    question_type = serializers.CharField(source="question.type", read_only=True)
    question_points = serializers.DecimalField(
        source="question.points", max_digits=5, decimal_places=2, read_only=True
    )
    selected_choices = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    correct_choices = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = (
            "id", "question", "question_text", "question_type", "question_points",
            "selected_choices", "text_answer", "correct_choices",
            "is_correct", "points_awarded", "feedback",
        )

    def get_correct_choices(self, obj) -> list:
        return [c.id for c in obj.question.choices.all() if c.is_correct]


class AttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    questions = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Attempt
        fields = (
            "id", "quiz", "quiz_title", "student", "student_name", "status",
            "started_at", "submitted_at", "score", "max_score", "questions", "answers",
        )

    def get_questions(self, obj) -> list:
        qs = obj.quiz.questions.prefetch_related("choices")
        return QuestionStudentSerializer(qs, many=True).data

    def get_answers(self, obj) -> list:
        qs = obj.answers.select_related("question").prefetch_related(
            "selected_choices", "question__choices"
        )
        return AnswerResultSerializer(qs, many=True).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        is_student = bool(request and request.user.role == User.Role.STUDENT)
        if instance.status == Attempt.Status.IN_PROGRESS:
            data.pop("answers")
            data.pop("score")
        else:
            data.pop("questions")
            if is_student and not instance.quiz.show_corrections:
                data["answers"] = []
            if is_student and instance.status != Attempt.Status.GRADED:
                data["score"] = None  # note provisoire masquée tant que la correction n'est pas finie
        return data


class AnswerInputSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    selected_choices = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=list
    )
    text_answer = serializers.CharField(required=False, allow_blank=True, default="")


class SubmitSerializer(serializers.Serializer):
    answers = AnswerInputSerializer(many=True)


class ManualGradeItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="ID de la réponse (Answer)")
    points_awarded = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0)
    feedback = serializers.CharField(required=False, allow_blank=True, default="")


class ManualGradeSerializer(serializers.Serializer):
    answers = ManualGradeItemSerializer(many=True, allow_empty=False)
