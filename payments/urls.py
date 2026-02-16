from django.urls import path
from .views import MockPaymentView
from .webhook import MockPaymentWebhookView

urlpatterns = [
    path("payments/orders/<int:order_id>/initiate/", MockPaymentView.as_view(), name="mock-pay"),
    path("payments/webhook/", MockPaymentWebhookView.as_view(), name="mock-webhook"),
]
