from django.urls import path
from . import views
urlpatterns = [
    path('', views.idea_feed_view, name='ideas'),
    path('<int:idea_id>/', views.idea_detail_view, name='idea_detail'),
]
