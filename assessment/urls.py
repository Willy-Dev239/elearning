from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("quizzes", views.QuizViewSet, basename="quiz")
router.register("questions", views.QuestionViewSet, basename="question")
router.register("attempts", views.AttemptViewSet, basename="attempt")

urlpatterns = [path("", include(router.urls))]
