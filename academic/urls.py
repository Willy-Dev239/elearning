from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("years", views.AcademicYearViewSet, basename="academic-year")
router.register("courses", views.CourseViewSet, basename="course")
router.register("enrollments", views.EnrollmentViewSet, basename="enrollment")
router.register("timetable", views.TimetableViewSet, basename="timetable")
router.register("grades", views.GradeViewSet, basename="grade")

urlpatterns = [
    path("transcript/", views.TranscriptView.as_view(), name="transcript"),
    path("", include(router.urls)),
]
