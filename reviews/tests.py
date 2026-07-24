from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from categories.models import Category
from products.models import Product
from .models import Review


class ReviewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='secret123',
        )
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Phone',
            description='A test phone',
            price='199.99',
            category=self.category,
            stock=10,
        )

    def test_create_and_list_reviews(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            '/api/reviews/',
            {'product_id': self.product.id, 'comment': 'Excellent product', 'rating': 5},
            format='json',
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(response.data['comment'], 'Excellent product')

        list_response = self.client.get('/api/reviews/')
        self.assertEqual(list_response.status_code, 200)
        self.assertGreaterEqual(len(list_response.data), 1)
