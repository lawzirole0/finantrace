from django.urls import path
from . import views

urlpatterns = [
    path('', views.connections_view, name='connections'),
    path('connect/', views.connect_platform_view, name='connect_platform'),
    path('<int:connection_id>/disconnect/', views.disconnect_platform_view, name='disconnect_platform'),
    path('<int:connection_id>/sync/', views.sync_connection_view, name='sync_connection'),
]
