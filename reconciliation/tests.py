from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from .models import DailyReport
from .services.trace_engine import TraceResult


class TraceResultTest(TestCase):
    def test_balanced_report(self):
        result = TraceResult(Decimal('100'), Decimal('50'), Decimal('30'), Decimal('120'))
        self.assertTrue(result.is_balanced)
        self.assertEqual(result.expected_closing, Decimal('120'))
        self.assertEqual(result.difference, Decimal('0'))
        self.assertEqual(result.get_suggestions(), [])

    def test_unbalanced_positive_difference(self):
        result = TraceResult(Decimal('100'), Decimal('50'), Decimal('30'), Decimal('130'))
        self.assertFalse(result.is_balanced)
        self.assertEqual(result.difference, Decimal('10'))
        suggestions = result.get_suggestions()
        self.assertTrue(any('Missing withdrawal' in s['title'] for s in suggestions))

    def test_unbalanced_negative_difference(self):
        result = TraceResult(Decimal('100'), Decimal('50'), Decimal('30'), Decimal('110'))
        self.assertFalse(result.is_balanced)
        self.assertEqual(result.difference, Decimal('-10'))
        suggestions = result.get_suggestions()
        self.assertTrue(any('Missing deposit' in s['title'] for s in suggestions))

    def test_to_context_includes_all_keys(self):
        result = TraceResult(Decimal('100'), Decimal('50'), Decimal('30'), Decimal('120'))
        ctx = result.to_context()
        self.assertIn('balanced', ctx)
        self.assertIn('opening', ctx)
        self.assertIn('deposits', ctx)
        self.assertIn('withdrawals', ctx)
        self.assertIn('closing', ctx)
        self.assertIn('expected_closing', ctx)
        self.assertIn('difference', ctx)
        self.assertIn('suggestions', ctx)


class DailyReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")

    def test_balanced_report_save(self):
        report = DailyReport.objects.create(
            user=self.user,
            opening_balance=Decimal('100'),
            total_deposits=Decimal('50'),
            total_withdrawals=Decimal('30'),
            closing_balance=Decimal('120'),
        )
        self.assertTrue(report.is_balanced)
        self.assertEqual(report.difference, Decimal('0'))

    def test_unbalanced_report_save(self):
        report = DailyReport.objects.create(
            user=self.user,
            opening_balance=Decimal('100'),
            total_deposits=Decimal('50'),
            total_withdrawals=Decimal('30'),
            closing_balance=Decimal('999'),
        )
        self.assertFalse(report.is_balanced)
        self.assertNotEqual(report.difference, Decimal('0'))

    def test_report_str(self):
        report = DailyReport.objects.create(
            user=self.user,
            opening_balance=Decimal('0'),
            total_deposits=Decimal('0'),
            total_withdrawals=Decimal('0'),
            closing_balance=Decimal('0'),
        )
        self.assertIn('Report #', str(report))
        self.assertIn('testuser', str(report))


class ReconciliationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.client.login(username='testuser', password='pass123')

    def test_new_report_get(self):
        response = self.client.get(reverse('new_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reconciliation/new_report.html')

    def test_trace_result_post_balanced(self):
        response = self.client.post(reverse('trace_result'), {
            'opening': '100',
            'deposits': '50',
            'withdrawals': '30',
            'closing': '120',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reconciliation/result.html')
        self.assertContains(response, 'Balanced!')

    def test_trace_result_post_unbalanced(self):
        response = self.client.post(reverse('trace_result'), {
            'opening': '100',
            'deposits': '50',
            'withdrawals': '30',
            'closing': '999',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reconciliation/result.html')

    def test_trace_result_decrements_trial(self):
        self.assertEqual(self.user.profile.trial_uses_remaining, 3)
        self.client.post(reverse('trace_result'), {
            'opening': '0', 'deposits': '0', 'withdrawals': '0', 'closing': '0',
        })
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.trial_uses_remaining, 2)

    def test_trace_result_get_redirects(self):
        response = self.client.get(reverse('trace_result'))
        self.assertRedirects(response, reverse('new_report'))

    def test_unauthenticated_redirect(self):
        self.client.logout()
        for url in [reverse('new_report'), reverse('trace_result')]:
            response = self.client.get(url)
            self.assertRedirects(response, f'/accounts/login/?next={url}')
