from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import MeView, RegisterView, UserViewSet
from courses.views import CourseViewSet, LessonViewSet
from payments.views import FeeViewSet, PaymentViewSet, StatsView
from quizzes.views import AttemptViewSet, QuizViewSet
from schools.views import ClassroomViewSet, EnrollmentViewSet, SchoolViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("schools", SchoolViewSet, basename="school")
router.register("classrooms", ClassroomViewSet, basename="classroom")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
router.register("courses", CourseViewSet, basename="course")
router.register("lessons", LessonViewSet, basename="lesson")
router.register("quizzes", QuizViewSet, basename="quiz")
router.register("attempts", AttemptViewSet, basename="attempt")
router.register("fees", FeeViewSet, basename="fee")
router.register("payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html")),
    path("admin/", admin.site.urls),
    path("api/auth/login/", TokenObtainPairView.as_view()),
    path("api/auth/refresh/", TokenRefreshView.as_view()),
    path("api/auth/register/", RegisterView.as_view()),
    path("api/auth/me/", MeView.as_view()),
    path("api/stats/", StatsView.as_view()),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("api/", include(router.urls)),
]
