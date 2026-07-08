from django.test import TestCase, Client
from django.urls import reverse


class LandingViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_landing_page(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing/index.html')

    def test_pricing_page(self):
        response = self.client.get(reverse('pricing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/pricing.html')

    def test_growth_guide(self):
        response = self.client.get(reverse('growth_guide'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing/growth_guide.html')
