from django.db import models

class Idea(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    RISK_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    INDUSTRY_CHOICES = [
        ('fintech', 'FinTech & SaaS'),
        ('energy', 'Sustainable Energy'),
        ('health', 'Health & Wellness'),
        ('edtech', 'EdTech'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    long_description = models.TextField(blank=True, help_text="Full analysis text")
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES, db_index=True)
    market_demand = models.IntegerField(help_text="Percentage 0-100")
    ease_of_entry = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, db_index=True)
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, default='medium', db_index=True)
    profit_range_min = models.IntegerField(help_text="Min yearly profit in USD")
    profit_range_max = models.IntegerField(help_text="Max yearly profit in USD")
    monthly_revenue_min = models.IntegerField(default=0, help_text="Est. monthly revenue min")
    monthly_revenue_max = models.IntegerField(default=0, help_text="Est. monthly revenue max")
    startup_cost_min = models.IntegerField(default=0, help_text="Min startup cost in USD")
    startup_cost_max = models.IntegerField(default=0, help_text="Max startup cost in USD")
    time_to_revenue = models.IntegerField(default=3, help_text="Months to first revenue")
    time_to_profit = models.IntegerField(default=6, help_text="Months to profitability")
    growth_potential = models.IntegerField(default=50, help_text="Long-term growth score 0-100")
    why_now = models.TextField(blank=True, help_text="Why this is a good time for this idea")
    steps_to_start = models.TextField(blank=True, help_text="Key steps to launch (one per line)")
    key_metrics = models.TextField(blank=True, help_text="KPIs to track (one per line)")
    icon = models.CharField(max_length=50, default="currency_exchange")
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['industry', 'is_active']),
            models.Index(fields=['risk_level', 'is_active']),
            models.Index(fields=['ease_of_entry', 'is_active']),
            models.Index(fields=['startup_cost_min', 'is_active']),
        ]

    def __str__(self):
        return self.title
