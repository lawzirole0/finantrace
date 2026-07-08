from django.urls import path
from . import views
urlpatterns = [
    path('', views.new_report_view, name='new_report'),
    path('result/', views.trace_result_view, name='trace_result'),
]
