from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("fees", views.FeeStructureViewSet, basename="fee")
router.register("installments", views.InstallmentViewSet, basename="installment")
router.register("payments", views.PaymentViewSet, basename="payment")

urlpatterns = [
    path("my-account/", views.MyAccountView.as_view(), name="my-account"),
    path("tracking/", views.TrackingView.as_view(), name="tracking"),
    path("webhook/", views.WebhookView.as_view(), name="payment-webhook"),
    path("", include(router.urls)),
]
