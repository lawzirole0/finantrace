from django.contrib import admin
from .models import PlatformConnection

@admin.register(PlatformConnection)
class PlatformConnectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'account_name', 'is_active', 'last_synced_at', 'created_at']
    list_filter = ['platform', 'is_active']
    search_fields = ['user__username', 'account_name', 'account_email']
