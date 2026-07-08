from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profession, Step, StepItem, UserProgress


class PathsModelsTest(TestCase):
    def setUp(self):
        self.prof = Profession.objects.create(slug='freelancer', name='Freelancer', description='Test')
        self.step = Step.objects.create(profession=self.prof, order=1, title='Step 1')
        self.item = StepItem.objects.create(step=self.step, text='Do something', order=1)

    def test_profession_str(self):
        self.assertEqual(str(self.prof), 'Freelancer')

    def test_step_str(self):
        self.assertIn('Freelancer', str(self.step))
        self.assertIn('Step 1', str(self.step))

    def test_step_item_str(self):
        self.assertEqual(str(self.item), 'Do something')

    def test_user_progress(self):
        user = User.objects.create_user(username='testuser', password='pass123')
        progress = UserProgress.objects.create(user=user, step_item=self.item, completed=True)
        self.assertTrue(progress.completed)
        self.assertIn('testuser', str(progress))
        self.assertIn('✓', str(progress))

    def test_step_ordering(self):
        Step.objects.create(profession=self.prof, order=2, title='Step 2')
        Step.objects.create(profession=self.prof, order=0, title='Step 0')
        steps = Step.objects.filter(profession=self.prof)
        self.assertEqual([s.order for s in steps], [0, 1, 2])


class PathsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.client.login(username='testuser', password='pass123')

    def test_path_view_get(self):
        response = self.client.get(reverse('paths'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'paths/path_detail.html')

    def test_path_view_creates_steps(self):
        response = self.client.get(reverse('paths'))
        self.assertIn('steps', response.context)
        self.assertGreater(len(response.context['steps']), 0)

    def test_path_view_progress(self):
        response = self.client.get(reverse('paths'))
        self.assertIn('progress_pct', response.context)
        self.assertIn('user_progress', response.context)
