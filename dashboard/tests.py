from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from reconciliation.models import DailyReport
from decimal import Decimal


class DashboardViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.client.login(username='testuser', password='pass123')

    def test_dashboard_get(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/index.html')

    def test_dashboard_context(self):
        DailyReport.objects.create(
            user=self.user, opening_balance=Decimal('0'),
            total_deposits=Decimal('0'), total_withdrawals=Decimal('0'),
            closing_balance=Decimal('0'),
        )
        response = self.client.get(reverse('dashboard'))
        self.assertIn('reports', response.context)
        self.assertIn('transactions', response.context)
        self.assertIn('path_progress', response.context)
        self.assertIn('profession_data', response.context)

    def test_dashboard_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("dashboard")}')
