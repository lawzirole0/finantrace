from django.db import models
from django.contrib.auth.models import User

class Profession(models.Model):
    slug = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default="work")

    def __str__(self):
        return self.name

class Step(models.Model):
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, related_name='steps', db_index=True)
    order = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['profession', 'order']),
        ]

    def __str__(self):
        return f"{self.profession.name} - Step {self.order}: {self.title}"

class StepItem(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='items', db_index=True)
    text = models.CharField(max_length=300)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['step', 'order']),
        ]

    def __str__(self):
        return self.text[:50]

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress', db_index=True)
    step_item = models.ForeignKey(StepItem, on_delete=models.CASCADE, db_index=True)
    completed = models.BooleanField(default=False, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'step_item']
        indexes = [
            models.Index(fields=['user', 'completed']),
            models.Index(fields=['step_item', 'completed']),
        ]

    def __str__(self):
        return f"{self.user.username} - {'✓' if self.completed else '○'} {self.step_item.text[:30]}"
