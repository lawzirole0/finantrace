from django.urls import path
from . import views
urlpatterns = [path('', views.path_view, name='paths')]
