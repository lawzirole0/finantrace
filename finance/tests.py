from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from .models import Transaction
from .services.calculator import get_cash_flow_summary


class TransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")

    def test_create_transaction(self):
        t = Transaction.objects.create(
            user=self.user,
            date='2024-01-15',
            vendor='Test Vendor',
            amount=Decimal('500.00'),
            transaction_type='income',
        )
        self.assertEqual(str(t), "Test Vendor - $500.00")
        self.assertEqual(t.status, 'pending')

    def test_transaction_ordering(self):
        Transaction.objects.create(user=self.user, date='2024-01-10', vendor='A', amount=1, transaction_type='income')
        Transaction.objects.create(user=self.user, date='2024-01-20', vendor='B', amount=2, transaction_type='income')
        qs = Transaction.objects.all()
        self.assertEqual(qs.first().vendor, 'B')
        self.assertEqual(qs.last().vendor, 'A')


class CalculatorServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")

    def _make_tx(self, amount, tx_type, status='pending'):
        return Transaction.objects.create(
            user=self.user, date='2024-01-15', vendor='V',
            amount=Decimal(str(amount)), transaction_type=tx_type, status=status,
        )

    def test_cash_flow_summary(self):
        self._make_tx(1000, 'income', 'matched')
        self._make_tx(500, 'income', 'matched')
        self._make_tx(300, 'expense', 'matched')
        self._make_tx(50, 'expense', 'discrepancy')

        qs = Transaction.objects.all()
        summary = get_cash_flow_summary(list(qs))

        self.assertEqual(summary['total_income'], Decimal('1500'))
        self.assertEqual(summary['total_expenses'], Decimal('350'))
        self.assertEqual(summary['net_profit'], Decimal('1150'))
        self.assertEqual(summary['matched_count'], 3)
        self.assertEqual(summary['discrepancy_count'], 1)
        self.assertEqual(summary['accuracy'], 75.0)

    def test_empty_transactions(self):
        summary = get_cash_flow_summary([])
        self.assertEqual(summary['total_income'], 0)
        self.assertEqual(summary['accuracy'], 100)


class FinanceViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.client.login(username='testuser', password='pass123')

    def test_finance_overview_get(self):
        response = self.client.get(reverse('finance'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finance/overview.html')

    def test_finance_overview_shows_transactions(self):
        Transaction.objects.create(
            user=self.user, date='2024-01-15', vendor='Shopify',
            amount=Decimal('1500'), transaction_type='income',
        )
        response = self.client.get(reverse('finance'))
        self.assertEqual(response.status_code, 200)
        transactions = response.context['transactions']
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].vendor, 'Shopify')
