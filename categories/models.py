from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return f"{self.parent.name + ' > ' if self.parent else ''}{self.name}"
