from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('pricing/', views.pricing_view, name='pricing'),
    path('guide/', views.growth_guide_view, name='growth_guide'),
]
