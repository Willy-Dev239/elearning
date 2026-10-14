from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
        # La racine redirige vers la documentation interactive
    path("", RedirectView.as_view(url="/api/docs/", permanent=False)),
    path("admin/", admin.site.urls),
    # Auth-Service
    path("api/v1/", include("accounts.urls")),
    # Academic-Service
    path("api/v1/academic/", include("academic.urls")),
    # Media-Service
    path("api/v1/media/", include("mediahub.urls")),
    # Billing-Service
    path("api/v1/billing/", include("billing.urls")),
    # Assessment-Service
    path("api/v1/assessment/", include("assessment.urls")),
    # Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
