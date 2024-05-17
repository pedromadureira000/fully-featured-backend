from django.urls import path

from fully_featured.payment.views import stripe_webhook

urlpatterns = [
    path('webhook/', stripe_webhook),
]
