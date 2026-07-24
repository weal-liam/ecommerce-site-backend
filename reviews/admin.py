from django.contrib import admin

from .models import Reply, Review


class ReplyInline(admin.TabularInline):
    model = Reply
    extra = 1


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    inlines = [ReplyInline]
    list_display = ('user', 'product', 'rating', 'reviewed_at', 'likes', 'dislikes')
    search_fields = ('comment', 'user__username', 'product__name')


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('user', 'review', 'replied_at', 'likes', 'dislikes')
    search_fields = ('message', 'user__username')
