from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile, CURRENCY_CHOICES, CURRENCY_SYMBOLS
from .context_processors import profile_context


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")

    def test_profile_created_on_user_creation(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)

    def test_profile_default_values(self):
        profile = self.user.profile
        self.assertEqual(profile.profession, 'freelancer')
        self.assertEqual(profile.currency, 'USD')
        self.assertEqual(profile.trial_uses_remaining, 3)
        self.assertEqual(profile.subscription_status, 'free')

    def test_trial_uses_percent(self):
        profile = self.user.profile
        self.assertEqual(profile.trial_uses_percent, 100.0)
        profile.trial_uses_remaining = 1
        self.assertAlmostEqual(profile.trial_uses_percent, 100 / 3)

    def test_profile_str(self):
        self.assertEqual(str(self.user.profile), "testuser - freelancer")


class LoginSignupViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="pass123")

    def test_login_get(self):
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)

    def test_signup_get(self):
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(reverse('account_logout'))
        self.assertRedirects(response, reverse('landing'))


class ContextProcessorTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="pass123")

    def test_anonymous_user(self):
        result = profile_context(type('req', (), {'user': type('u', (), {'is_authenticated': False})()})())
        self.assertEqual(result['currency_code'], 'NGN')
        self.assertEqual(result['currency_symbol'], '₦')

    def test_authenticated_user(self):
        self.client.login(username='testuser', password='pass123')
        request = type('req', (), {'user': self.user, 'method': 'GET'})()
        result = profile_context(request)
        self.assertEqual(result['currency_code'], 'USD')


class CurrencyTagsTest(TestCase):
    def test_currency_filter_integer(self):
        from django.template import Template, Context
        t = Template("{% load currency_tags %}{{ 5000|currency:'USD' }}")
        rendered = t.render(Context({}))
        self.assertEqual(rendered, "$5,000")

    def test_currency_filter_decimal(self):
        from django.template import Template, Context
        t = Template("{% load currency_tags %}{{ 1234.56|currency:'EUR' }}")
        rendered = t.render(Context({}))
        self.assertEqual(rendered, "€1,234.56")

    def test_currency_filter_zero(self):
        from django.template import Template, Context
        t = Template("{% load currency_tags %}{{ 0|currency:'USD' }}")
        rendered = t.render(Context({}))
        self.assertEqual(rendered, "$0")

    def test_curr_symbol_filter(self):
        from django.template import Template, Context
        t = Template("{% load currency_tags %}{{ 'JPY'|curr_symbol }}")
        rendered = t.render(Context({}))
        self.assertEqual(rendered, "¥")

    def test_curr_symbol_unknown(self):
        from django.template import Template, Context
        t = Template("{% load currency_tags %}{{ 'XXX'|curr_symbol }}")
        rendered = t.render(Context({}))
        self.assertEqual(rendered, "$")


class CURRENCY_SYMBOLS_Test(TestCase):
    def test_all_currencies_have_symbols(self):
        for code, _ in CURRENCY_CHOICES:
            self.assertIn(code, CURRENCY_SYMBOLS, f"Missing symbol for {code}")
            self.assertTrue(CURRENCY_SYMBOLS[code], f"Empty symbol for {code}")
