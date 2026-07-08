from django.urls import path
from landing.views import pricing_view
from . import views

urlpatterns = [
    path('', pricing_view, name='payments_pricing'),
    path('subscribe/', views.subscribe_view, name='subscribe'),
    path('callback/', views.callback_view, name='paystack_callback'),
    path('webhook/', views.webhook_view, name='paystack_webhook'),
]
