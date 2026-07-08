from django.urls import path
from . import views
urlpatterns = [path('', views.finance_overview_view, name='finance')]
