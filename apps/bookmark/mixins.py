"""DRF mixins for bookmark serializer context."""
from .services import user_bookmark_task_ids


class BookmarkSerializerContextMixin:
    """Attach prefetched bookmark ids for list/retrieve serializers."""

    bookmark_context_actions = ('list', 'retrieve', 'bookmarked', 'mine')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        action = getattr(self, 'action', None)
        if user.is_authenticated and action in self.bookmark_context_actions:
            context['user_bookmark_task_ids'] = user_bookmark_task_ids(user)
        return context
