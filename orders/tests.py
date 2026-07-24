from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from unittest.mock import patch

from users.models import User
from products.models import Product
from cart.models import Cart, CartItem


class CheckoutTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='alice', password='password')
        self.product = Product.objects.create(name='Test', description='x', price='9.99')
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    @patch('payments.services.create_checkout_session')
    def test_checkout_creates_order_and_returns_session(self, mock_create):
        mock_create.return_value.id = 'sess_123'
        self.client.force_authenticate(user=self.user)

        url = '/orders/checkout'
        resp = self.client.post(url, {}, format='json')

        self.assertEqual(resp.status_code, 201)
        self.assertIn('order', resp.data)
        self.assertEqual(resp.data['id'], 'sess_123')

    def test_checkout_empty_cart(self):
        # clear cart
        CartItem.objects.all().delete()
        self.client.force_authenticate(user=self.user)
        url = '/orders/checkout'
        resp = self.client.post(url, {}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.data)

