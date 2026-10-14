from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("materials", views.MaterialViewSet, basename="material")

urlpatterns = [
    path("courses/<int:course_id>/progress/", views.CourseProgressView.as_view(), name="course-progress"),
    path("", include(router.urls)),
]
