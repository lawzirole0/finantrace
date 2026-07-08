from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import CURRENCY_CHOICES


class SettingsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.client.login(username='testuser', password='pass123')

    def test_settings_get(self):
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/index.html')
        self.assertIn('currency_choices', response.context)

    def test_settings_post_valid_currency(self):
        response = self.client.post(reverse('settings'), {'currency': 'EUR'})
        self.assertRedirects(response, reverse('settings'))
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.currency, 'EUR')

    def test_settings_post_invalid_currency(self):
        response = self.client.post(reverse('settings'), {'currency': 'INVALID'})
        self.assertRedirects(response, reverse('settings'))
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.currency, 'USD')

    def test_settings_all_currencies(self):
        for code, _ in CURRENCY_CHOICES:
            self.client.post(reverse('settings'), {'currency': code})
            self.user.profile.refresh_from_db()
            self.assertEqual(self.user.profile.currency, code, f"Failed to set currency {code}")
