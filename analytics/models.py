from django.db import models

from products.models import Product


# Create your models here.
class ProductView(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=100, null=True)