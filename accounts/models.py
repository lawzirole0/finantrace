from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

CURRENCY_CHOICES = [
    ('USD', 'USD ($) - US Dollar'),
    ('EUR', 'EUR (€) - Euro'),
    ('GBP', 'GBP (£) - British Pound'),
    ('JPY', 'JPY (¥) - Japanese Yen'),
    ('CNY', 'CNY (¥) - Chinese Yuan'),
    ('INR', 'INR (₹) - Indian Rupee'),
    ('CAD', 'CAD ($) - Canadian Dollar'),
    ('AUD', 'AUD ($) - Australian Dollar'),
    ('BRL', 'BRL (R$) - Brazilian Real'),
    ('MXN', 'MXN ($) - Mexican Peso'),
    ('KRW', 'KRW (₩) - South Korean Won'),
    ('SGD', 'SGD ($) - Singapore Dollar'),
    ('HKD', 'HKD ($) - Hong Kong Dollar'),
    ('CHF', 'CHF (Fr) - Swiss Franc'),
    ('SEK', 'SEK (kr) - Swedish Krona'),
    ('NOK', 'NOK (kr) - Norwegian Krone'),
    ('DKK', 'DKK (kr) - Danish Krone'),
    ('NZD', 'NZD ($) - New Zealand Dollar'),
    ('ZAR', 'ZAR (R) - South African Rand'),
    ('TRY', 'TRY (₺) - Turkish Lira'),
    ('RUB', 'RUB (₽) - Russian Ruble'),
    ('PLN', 'PLN (zł) - Polish Zloty'),
    ('THB', 'THB (฿) - Thai Baht'),
    ('IDR', 'IDR (Rp) - Indonesian Rupiah'),
    ('MYR', 'MYR (RM) - Malaysian Ringgit'),
    ('PHP', 'PHP (₱) - Philippine Peso'),
    ('AED', 'AED (د.إ) - UAE Dirham'),
    ('SAR', 'SAR (﷼) - Saudi Riyal'),
    ('ILS', 'ILS (₪) - Israeli Shekel'),
    ('VND', 'VND (₫) - Vietnamese Dong'),
    ('NGN', 'NGN (₦) - Nigerian Naira'),
    ('KES', 'KES (KSh) - Kenyan Shilling'),
    ('EGP', 'EGP (E£) - Egyptian Pound'),
    ('PKR', 'PKR (₨) - Pakistani Rupee'),
    ('BDT', 'BDT (৳) - Bangladeshi Taka'),
]

CURRENCY_SYMBOLS = {code: label.split('(')[1].split(')')[0] if '(' in label else code for code, label in CURRENCY_CHOICES}

class UserProfile(models.Model):
    PROFESSION_CHOICES = [
        ('freelancer', 'Freelancer'),
        ('retail', 'Retail'),
        ('service', 'Service'),
        ('food', 'Food'),
        ('creator', 'Creator'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', db_index=True)
    profession = models.CharField(max_length=20, choices=PROFESSION_CHOICES, default='freelancer', db_index=True)
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default='USD')
    trial_uses_remaining = models.IntegerField(default=3)
    device_id = models.CharField(max_length=100, blank=True, null=True)
    subscription_status = models.CharField(max_length=20, default='free', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'profession']),
            models.Index(fields=['subscription_status', 'profession']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.profession}"

    @property
    def trial_uses_percent(self):
        return (self.trial_uses_remaining / 3) * 100

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
