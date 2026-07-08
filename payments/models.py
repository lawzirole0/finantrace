from django.db import models
from django.contrib.auth.models import User

class Subscription(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('startup', 'Startup'),
        ('growing', 'Growing'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription', db_index=True)
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='free', db_index=True)
    paystack_customer_code = models.CharField(max_length=100, blank=True, help_text="Paystack customer reference (cus_xxx)")
    paystack_subscription_code = models.CharField(max_length=100, blank=True, help_text="Paystack subscription reference (sub_xxx)")
    paystack_authorization_code = models.CharField(max_length=100, blank=True, help_text="Reusable card auth code (auth_xxx)")
    paystack_email = models.EmailField(max_length=254, blank=True, help_text="Email used for Paystack transactions")
    is_active = models.BooleanField(default=False, db_index=True)
    started_at = models.DateTimeField(auto_now_add=True)
    renews_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['plan', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.plan}"
