from django.contrib import admin

from .models import ShippingOption


@admin.register(ShippingOption)
class ShippingOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'estimated_days', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
