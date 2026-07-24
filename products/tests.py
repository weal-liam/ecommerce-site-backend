from django.test import TestCase
from users.models import User
# Create your tests here.
class ProductTestCase(TestCase):
    def setUp(self):
        User.objects.create_superuser(username='testuser', email='testuser@example.com', password='testpass')

    def test_product_creation(self):
        user = User.objects.get(username='testuser')
        self.client.force_login(user)
        response = self.client.post(
            '/api/products/create/',
            {
                'name': 'Test Product',
                'description': 'This is a test product.',
                'image_url': 'http://example.com/image.jpg',
                'price': '9.99',
                'category': 'Test Category',
                'stock': 10,
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], 'Test Product')
        self.assertEqual(data['category'], 'Test Category')
        self.assertEqual(data['image_url'], 'http://example.com/image.jpg')

    def test_bulk_product_creation_with_image_url(self):
        user = User.objects.get(username='testuser')
        self.client.force_login(user)
        payload = [
            {
                'name': 'Test Product 1',
                'description': 'This is a test product 1.',
                'image_url': 'http://example.com/image1.jpg',
                'price': '9.99',
                'category': 'Test Category',
                'stock': 10,
            },
            {
                'name': 'Test Product 2',
                'description': 'This is a test product 2.',
                'image_url': 'http://example.com/image2.jpg',
                'price': '19.99',
                'category': 'Test Category',
                'stock': 5,
            },
        ]
        response = self.client.post(
            '/api/products/create/',
            payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['category'], 'Test Category')
        self.assertEqual(data[1]['category'], 'Test Category')
