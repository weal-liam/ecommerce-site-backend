from django.test import TestCase
from rest_framework.test import APIClient

from .models import ShippingOption


class ShippingOptionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_and_list_shipping_options(self):
        response = self.client.post(
            '/api/shipping/',
            {'name': 'Express', 'price': '12.50', 'estimated_days': 2, 'is_active': True},
            format='json',
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(ShippingOption.objects.count(), 1)

        list_response = self.client.get('/api/shipping/')
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data[0]['name'], 'Express')
