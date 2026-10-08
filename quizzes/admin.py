from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import Attempt, Choice, Question, Quiz


class QuestionInline(TabularInline):
    model = Question
    extra = 1
    fields = ("text", "order")
    show_change_link = True


class ChoiceInline(TabularInline):
    model = Choice
    extra = 3
    fields = ("text", "is_correct")


@admin.register(Quiz)
class QuizAdmin(ModelAdmin):
    list_display = ("title", "course", "pass_mark")
    list_filter = ("course",)
    search_fields = ("title",)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ("text", "quiz", "order")
    list_filter = ("quiz",)
    search_fields = ("text",)
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(ModelAdmin):
    list_display = ("text", "question", "is_correct")
    list_filter = ("is_correct",)


@admin.register(Attempt)
class AttemptAdmin(ModelAdmin):
    list_display = ("student", "quiz", "note", "result", "created")
    list_filter = ("quiz",)
    search_fields = ("student__username", "student__last_name")

    @display(description="Note")
    def note(self, obj):
        return f"{obj.score} / {obj.total} ({obj.percent} %)"

    @display(description="Résultat", label={"Réussi": "success", "Non réussi": "danger"})
    def result(self, obj):
        return "Réussi" if obj.passed else "Non réussi"
