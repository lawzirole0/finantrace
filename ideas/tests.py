from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Idea
from .services.ai_generator import _fallback_ideas, _parse_response


class IdeaModelTest(TestCase):
    def setUp(self):
        self.idea = Idea.objects.create(
            title="Test SaaS",
            description="A test business idea",
            industry="fintech",
            market_demand=85,
            ease_of_entry="easy",
            risk_level="low",
            profit_range_min=10000,
            profit_range_max=50000,
        )

    def test_idea_creation(self):
        self.assertEqual(str(self.idea), "Test SaaS")
        self.assertTrue(self.idea.is_active)

    def test_idea_defaults(self):
        self.assertEqual(self.idea.monthly_revenue_min, 0)
        self.assertEqual(self.idea.time_to_revenue, 3)
        self.assertEqual(self.idea.growth_potential, 50)


class IdeasViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.client.login(username='testuser', password='pass123')
        self.idea = Idea.objects.create(
            title="FinTech App", description="A fintech idea",
            industry="fintech", market_demand=90, ease_of_entry="medium",
            risk_level="medium", profit_range_min=20000, profit_range_max=100000,
            steps_to_start="Step 1\nStep 2\nStep 3",
            key_metrics="Metric 1\nMetric 2",
        )

    def test_idea_feed_get(self):
        response = self.client.get(reverse('ideas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ideas/feed.html')
        self.assertContains(response, 'FinTech App')

    @patch('ideas.views.get_personalized_ideas', return_value=_fallback_ideas('freelancer'))
    def test_idea_feed_post_ai(self, mock_ai):
        response = self.client.post(reverse('ideas'), {'get_ai_suggestions': '1', 'interests': 'AI, SaaS'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('ai_ideas', response.context)
        self.assertEqual(len(response.context['ai_ideas']), 3)
        mock_ai.assert_called_once()

    def test_idea_detail(self):
        response = self.client.get(reverse('idea_detail', args=[self.idea.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ideas/detail.html')
        self.assertContains(response, 'FinTech App')
        self.assertIn('match_score', response.context)

    def test_idea_detail_steps_parsed(self):
        response = self.client.get(reverse('idea_detail', args=[self.idea.id]))
        self.assertEqual(len(response.context['steps']), 3)
        self.assertEqual(len(response.context['metrics']), 2)

    def test_idea_detail_404(self):
        response = self.client.get(reverse('idea_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)


class AIGeneratorFallbackTest(TestCase):
    def test_fallback_returns_three_ideas(self):
        ideas = _fallback_ideas("freelancer")
        self.assertEqual(len(ideas), 3)

    def test_fallback_contains_required_fields(self):
        ideas = _fallback_ideas("creator")
        required = {'title', 'description', 'market_demand', 'ease', 'profit_range',
                     'startup_cost', 'time_to_revenue', 'time_to_profit', 'growth_potential', 'risk'}
        for idea in ideas:
            self.assertTrue(required.issubset(idea.keys()), f"Missing fields in {idea['title']}")

    def test_fallback_interpolates_profession(self):
        ideas = _fallback_ideas("retail")
        for idea in ideas:
            self.assertIn('retail', idea['title'].lower() or idea['description'].lower())

    def test_parse_response_valid_json(self):
        text = '[{"title": "Test Idea", "description": "Desc", "market_demand": 80}]'
        result = _parse_response(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Test Idea')

    def test_parse_response_invalid_falls_back(self):
        result = _parse_response("not json at all")
        self.assertEqual(len(result), 3)  # falls back to hardcoded
