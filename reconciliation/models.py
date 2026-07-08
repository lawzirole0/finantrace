from django.db import models
from django.contrib.auth.models import User

class DailyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', db_index=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2)
    total_deposits = models.DecimalField(max_digits=12, decimal_places=2)
    total_withdrawals = models.DecimalField(max_digits=12, decimal_places=2)
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2)
    expected_closing = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    difference = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    is_balanced = models.BooleanField(editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_balanced']),
            models.Index(fields=['user', 'created_at']),
        ]

    def save(self, *args, **kwargs):
        self.expected_closing = self.opening_balance + self.total_deposits - self.total_withdrawals
        self.difference = self.closing_balance - self.expected_closing
        self.is_balanced = (self.difference == 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Report #{self.id} - {self.user.username} - {'✓' if self.is_balanced else '✗'}"
