from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(max_length=100,unique=True)
    is_customer = models.BooleanField(default=True)
    is_vendor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user-detail',kwargs={'pk': self.pk})