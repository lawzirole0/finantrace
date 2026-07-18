from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('landing.urls')),
    path('accounts/', include('allauth.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('reconciliation/', include('reconciliation.urls')),
    path('finance/', include('finance.urls')),
    path('paths/', include('paths.urls')),
    path('ideas/', include('ideas.urls')),
    path('roadmap/', include('roadmap.urls')),
    path('payments/', include('payments.urls')),
    path('settings/', include('settings_app.urls')),
    path('connections/', include('connections.urls')),
]
