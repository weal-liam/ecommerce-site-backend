from django.db import models

from products.models import Product
from users.models import User


class Review(models.Model):
    class Rating(models.IntegerChoices):
        ZER0_STAR = 0
        ONE_STAR = 1
        TWO_STAR = 2
        THREE_STAR = 3
        FOUR_STAR = 4
        FIVE_STAR = 5

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    comment = models.CharField(max_length=255)
    rating = models.IntegerField(choices=Rating.choices, default=Rating.ZER0_STAR)
    reviewed_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveBigIntegerField(default=0)
    dislikes = models.PositiveBigIntegerField(default=0)

    class Meta:
        ordering = ['-reviewed_at']

    def __str__(self):
        return f"{self.user.username} reviewed {self.product.name}" 


class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="replies")
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="replies")
    message = models.CharField(max_length=255)
    replied_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveBigIntegerField(default=0)
    dislikes = models.PositiveBigIntegerField(default=0)

    class Meta:
        ordering = ['-replied_at']

    def __str__(self):
        return f"Reply by {self.user.username}"