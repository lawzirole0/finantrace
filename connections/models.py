from django.db import models
from django.contrib.auth.models import User
import json

class PlatformConnection(models.Model):
    PLATFORM_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('shopify', 'Shopify'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('linkedin', 'LinkedIn'),
        ('etsy', 'Etsy'),
        ('square', 'Square'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connections', db_index=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, db_index=True)
    label = models.CharField(max_length=100, blank=True, help_text="Friendly name for this connection")
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    account_id = models.CharField(max_length=200, blank=True)
    account_name = models.CharField(max_length=200, blank=True)
    account_email = models.EmailField(max_length=200, blank=True)
    metadata = models.TextField(blank=True, help_text="JSON blob for platform-specific data")
    is_active = models.BooleanField(default=True, db_index=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'platform', 'account_id']
        ordering = ['platform', 'account_name']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['platform', 'is_active']),
            models.Index(fields=['user', 'last_synced_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_platform_display()} ({self.account_name or self.account_id})"

    def get_metadata_dict(self):
        if self.metadata:
            try:
                return json.loads(self.metadata)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_metadata_dict(self, data):
        self.metadata = json.dumps(data)
