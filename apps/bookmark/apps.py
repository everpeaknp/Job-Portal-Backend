"""Bookmark app configuration."""
from django.apps import AppConfig


class BookmarkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bookmark'
    verbose_name = 'Bookmarks'
