"""Admin for unified bookmarks."""
from django.contrib import admin

from apps.tasks.listing import get_listing_kind

from .models import Bookmark


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'listing_kind', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'task__title', 'task__slug']
    ordering = ['-created_at']
    autocomplete_fields = ['user', 'task']

    @admin.display(description='Listing kind')
    def listing_kind(self, obj):
        return get_listing_kind(obj.task.tags)
