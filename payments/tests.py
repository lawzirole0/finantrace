from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Subscription


class SubscriptionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")

    def test_free_subscription_defaults(self):
        sub = Subscription.objects.create(user=self.user)
        self.assertEqual(sub.plan, 'free')
        self.assertFalse(sub.is_active)
        self.assertEqual(sub.paystack_customer_code, '')
        self.assertEqual(sub.paystack_subscription_code, '')
        self.assertEqual(sub.paystack_authorization_code, '')
        self.assertEqual(sub.paystack_email, '')

    def test_subscription_str(self):
        sub = Subscription.objects.create(user=self.user, plan='startup', is_active=True)
        self.assertEqual(str(sub), "testuser - startup")

    def test_paystack_plan_fields(self):
        sub = Subscription.objects.create(
            user=self.user,
            plan='growing',
            paystack_customer_code='cus_test123',
            paystack_subscription_code='sub_test456',
            paystack_authorization_code='auth_test789',
            paystack_email='test@example.com',
            is_active=True,
        )
        self.assertEqual(sub.paystack_customer_code, 'cus_test123')
        self.assertEqual(sub.paystack_subscription_code, 'sub_test456')
        self.assertEqual(sub.paystack_authorization_code, 'auth_test789')


class SubscribeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123', email='user@example.com')
        self.client.login(username='testuser', password='pass123')

    def test_subscribe_get_redirects(self):
        response = self.client.get(reverse('subscribe'))
        self.assertRedirects(response, reverse('payments_pricing'))

    def test_subscribe_invalid_plan(self):
        response = self.client.post(reverse('subscribe'), {'plan': 'invalid'})
        self.assertRedirects(response, reverse('payments_pricing'))

    @patch('payments.services.paystack.initialize_transaction')
    def test_subscribe_creates_subscription(self, mock_init):
        mock_init.return_value = {
            'status': True,
            'data': {'authorization_url': 'https://checkout.paystack.com/test_ref'},
        }
        response = self.client.post(reverse('subscribe'), {'plan': 'startup'})
        sub = Subscription.objects.get(user=self.user)
        self.assertEqual(sub.plan, 'startup')
        mock_init.assert_called_once()

    def test_subscribe_view_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('subscribe'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("subscribe")}')


class CallbackViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.client.login(username='testuser', password='pass123')

    def test_callback_without_reference(self):
        response = self.client.get(reverse('paystack_callback'))
        self.assertRedirects(response, reverse('dashboard'))

    @patch('payments.services.paystack.create_subscription')
    @patch('payments.services.paystack.verify_transaction')
    def test_callback_with_reference(self, mock_verify, mock_sub):
        mock_verify.return_value = {
            'status': True,
            'data': {
                'status': 'success',
                'customer': {'customer_code': 'cus_test', 'email': 'test@example.com'},
                'authorization': {'authorization_code': 'auth_test'},
                'metadata': {'plan': 'startup'},
            },
        }
        mock_sub.return_value = {
            'status': True,
            'data': {'subscription_code': 'sub_test'},
        }
        response = self.client.get(reverse('paystack_callback'), {'reference': 'test_ref_123'})
        self.assertRedirects(response, reverse('dashboard'))
        sub = Subscription.objects.get(user=self.user)
        self.assertTrue(sub.is_active)
        self.assertEqual(sub.plan, 'startup')
        self.assertEqual(sub.paystack_customer_code, 'cus_test')


class WebhookViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_returns_405(self):
        response = self.client.get(reverse('paystack_webhook'))
        self.assertEqual(response.status_code, 405)

    def test_post_invalid_signature_returns_401(self):
        response = self.client.post(
            reverse('paystack_webhook'),
            content_type='application/json',
            data='{"event": "test"}',
            HTTP_X_PAYSTACK_SIGNATURE='invalid',
        )
        self.assertEqual(response.status_code, 401)
