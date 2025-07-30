from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()
# Create your models here.
class Payment(models.Model):
    session_id = models.CharField(max_length=200)
    owner = models.CharField(max_length=50)
    status = models.CharField(max_length=10,default='incomplete')
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.owner.name}-{self.amount}'

    def get_absolute_url(self):
        return reverse('invoice-detail',kwargs={'pk':self.pk})
