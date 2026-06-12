"""Freelancer (tasker) profile helpers and public slug lookup."""
import re
import uuid

from django.db.models import Q

from .models import User


def _freelancer_eligible_users():
    return (
        User.objects.filter(
            role='tasker',
            is_active=True,
            account_suspended=False,
        )
        .prefetch_related('skills', 'badges')
    )


def get_freelancer_user_by_slug(slug: str) -> User | None:
    """Resolve tasker from public profile URL segment (username, id, or email local-part)."""
    normalized = (slug or '').strip().lower()
    if not normalized:
        return None

    queryset = _freelancer_eligible_users()

    user = queryset.filter(username__iexact=normalized).first()
    if user:
        return user

    try:
        user = queryset.filter(id=uuid.UUID(normalized)).first()
        if user:
            return user
    except ValueError:
        pass

    email_local_pattern = rf'^{re.escape(normalized)}@'
    return queryset.filter(email__iregex=email_local_pattern).first()


def freelancer_public_slug(user: User) -> str:
    return (user.username or str(user.id)).strip().lower()
