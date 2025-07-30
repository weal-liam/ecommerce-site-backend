from django.db import models
from django.urls import reverse

from categories.models import Category

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    image_url = models.URLField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True)
    stock = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_image(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product-detail',kwargs={'pk': self.pk})