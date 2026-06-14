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


def is_freelancer_public_profile_ready(user: User) -> bool:
    """True when the tasker has filled in enough public profile data to display."""
    if (user.bio or '').strip() or (user.tagline or '').strip():
        return True
    if user.profile_image:
        return True
    if user.hourly_rate and float(user.hourly_rate) > 0:
        return True
    if (user.tasks_completed or 0) > 0 or (user.total_reviews or 0) > 0:
        return True
    if (user.city or '').strip():
        return True

    from .serializers import _profile_meta_from_user

    specialization, profile_type = _profile_meta_from_user(user)
    if (specialization or '').strip() or (profile_type or '').strip():
        return True

    for skill in user.skills.all():
        category = (skill.category or 'skill').strip().lower()
        name = (skill.name or '').strip()
        if not name:
            continue
        if category in {'skill', 'education', 'experience', 'language', 'transport', 'award'}:
            return True

    return False


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
