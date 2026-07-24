from django.test import TestCase
from django.urls import reverse

from users.models import User


class CookieAuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='cookieuser',
            email='cookie@example.com',
            password='StrongPass123',
        )

    def test_login_sets_httponly_auth_cookies(self):
        response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'cookieuser', 'password': 'StrongPass123'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertTrue(response.cookies['access_token']['httponly'])
        self.assertTrue(response.cookies['refresh_token']['httponly'])

    def test_me_endpoint_accepts_cookie_auth(self):
        self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'cookieuser', 'password': 'StrongPass123'},
            format='json',
        )

        response = self.client.get(reverse('user-me'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user']['email'], 'cookie@example.com')
