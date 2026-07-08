from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import PlatformConnection


class PlatformConnectionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")

    def test_create_connection(self):
        conn = PlatformConnection.objects.create(
            user=self.user,
            platform='stripe',
            label='My Stripe',
            account_name='Test Account',
            account_email='test@example.com',
            access_token='tok_test',
            is_active=True,
        )
        self.assertEqual(str(conn), "testuser - Stripe (Test Account)")
        self.assertEqual(conn.get_platform_display(), 'Stripe')

    def test_metadata_json(self):
        conn = PlatformConnection.objects.create(
            user=self.user, platform='shopify',
            account_name='Shop', metadata='{"shop_id": 123}',
        )
        self.assertEqual(conn.get_metadata_dict(), {'shop_id': 123})
        conn.set_metadata_dict({'shop_id': 456})
        conn.save()
        conn.refresh_from_db()
        self.assertIn('456', conn.metadata)

    def test_unique_together(self):
        PlatformConnection.objects.create(
            user=self.user, platform='instagram', account_id='abc123',
        )
        with self.assertRaises(Exception):
            PlatformConnection.objects.create(
                user=self.user, platform='instagram', account_id='abc123',
            )


class ConnectionsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.client.login(username='testuser', password='pass123')

    def test_connections_list_empty(self):
        response = self.client.get(reverse('connections'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'connections/index.html')

    def test_connections_list_with_data(self):
        PlatformConnection.objects.create(user=self.user, platform='paypal', account_name='My PayPal')
        response = self.client.get(reverse('connections'))
        self.assertContains(response, 'My PayPal')

    def test_connect_platform_get(self):
        response = self.client.get(reverse('connect_platform'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'connections/connect.html')

    def test_connect_platform_post_success(self):
        response = self.client.post(reverse('connect_platform'), {
            'platform': 'stripe',
            'label': 'My Stripe',
            'account_name': 'Acme Inc',
            'account_email': 'acme@example.com',
        })
        self.assertRedirects(response, reverse('connections'))
        self.assertTrue(PlatformConnection.objects.filter(user=self.user, platform='stripe').exists())

    def test_connect_platform_post_invalid(self):
        response = self.client.post(reverse('connect_platform'), {'platform': 'invalid'})
        self.assertRedirects(response, reverse('connect_platform'))

    def test_connect_platform_duplicate(self):
        PlatformConnection.objects.create(
            user=self.user, platform='stripe', account_id='dup@example.com',
        )
        response = self.client.post(reverse('connect_platform'), {
            'platform': 'stripe', 'account_email': 'dup@example.com',
        })
        self.assertRedirects(response, reverse('connections'))

    def test_disconnect_platform(self):
        conn = PlatformConnection.objects.create(user=self.user, platform='tiktok', account_name='TikTok')
        response = self.client.post(reverse('disconnect_platform', args=[conn.id]))
        self.assertRedirects(response, reverse('connections'))
        self.assertFalse(PlatformConnection.objects.filter(id=conn.id).exists())

    def test_disconnect_other_users_connection(self):
        other = User.objects.create_user(username='other', password='pass123')
        conn = PlatformConnection.objects.create(user=other, platform='etsy', account_name='Other')
        response = self.client.post(reverse('disconnect_platform', args=[conn.id]))
        self.assertEqual(response.status_code, 404)

    def test_sync_connection(self):
        conn = PlatformConnection.objects.create(user=self.user, platform='linkedin', account_name='Linked')
        response = self.client.post(reverse('sync_connection', args=[conn.id]))
        self.assertRedirects(response, reverse('connections'))
        conn.refresh_from_db()
        self.assertIsNotNone(conn.last_synced_at)


class ConnectionTagsTest(TestCase):
    def test_dict_key_filter(self):
        from django.template import Template, Context
        t = Template("{% load connection_tags %}{{ data|dict_key:'color' }}")
        rendered = t.render(Context({'data': {'color': 'blue', 'size': 'big'}}))
        self.assertEqual(rendered, "blue")

    def test_dict_key_missing(self):
        from django.template import Template, Context
        t = Template("{% load connection_tags %}{{ data|dict_key:'missing' }}")
        rendered = t.render(Context({'data': {'color': 'blue'}}))
        self.assertEqual(rendered, "{}")
