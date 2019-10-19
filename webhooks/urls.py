from django.urls import path, include
from . import views

urlpatterns = [
    path('webhook-handler/', views.webhook_handler, name='webhook_handler'),
    path('stripe-webhook-handler/', views.stripe_webhook_handler, name='stripe_webhook_handler'),
]
