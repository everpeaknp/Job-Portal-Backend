"""Unified bookmark model (proxy over TaskBookmark)."""
from apps.tasks.models import TaskBookmark


class Bookmark(TaskBookmark):
    """User bookmark on any marketplace listing (task, job, project, service)."""

    class Meta:
        proxy = True
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'
