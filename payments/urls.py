from django.urls import path
from .views import CreatePaymentView, CashfreeWebhookView


urlpatterns = [
    path(
        "create/",
        CreatePaymentView.as_view(),
        name="create-payment",
    ),
    path(
        "webhook/",
        CashfreeWebhookView.as_view(),
        name="cashfree-webhook",
    )
]   