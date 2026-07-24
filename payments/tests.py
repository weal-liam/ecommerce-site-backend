from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch

from users.models import User
from payments.models import Payment


class PaymentConfirmationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='alice', password='password')
        self.client.force_authenticate(user=self.user)

    @patch('payments.views.stripe.checkout.Session.retrieve')
    def test_confirm_order_is_idempotent(self, mock_retrieve):
        mock_retrieve.return_value = type('Session', (), {
            'payment_status': 'paid',
            'amount_total': 1999,
            'metadata': {'order_id': 'order_123'},
        })()

        url = '/api/payments/confirm?session_id=sess_123'
        first = self.client.get(url)
        second = self.client.get(url)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(Payment.objects.filter(session_id='sess_123').count(), 1)
        self.assertEqual(first.data['payment']['id'], second.data['payment']['id'])
        self.assertEqual(first.data['payment']['session_id'], 'sess_123')
