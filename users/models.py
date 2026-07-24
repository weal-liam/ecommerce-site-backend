from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(max_length=100, unique=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    profile_image_url = models.URLField(blank=True, null=True)
    is_customer = models.BooleanField(default=True)
    is_vendor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user-detail',kwargs={'pk': self.pk})