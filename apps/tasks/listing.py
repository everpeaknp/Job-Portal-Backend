"""Dashboard listing kinds stored on Task.tags (listing:service|project|job)."""

from django.db import connection

LISTING_TAG_PREFIX = 'listing:'

LISTING_KIND_TASK = 'task'
LISTING_KIND_SERVICE = 'service'
LISTING_KIND_PROJECT = 'project'
LISTING_KIND_JOB = 'job'

LISTING_KIND_CHOICES = (
    LISTING_KIND_SERVICE,
    LISTING_KIND_PROJECT,
    LISTING_KIND_JOB,
)

LISTING_KIND_CATEGORY_CHOICES = (
    (LISTING_KIND_TASK, 'Task'),
    (LISTING_KIND_SERVICE, 'Service'),
    (LISTING_KIND_PROJECT, 'Project'),
    (LISTING_KIND_JOB, 'Job'),
)


def listing_tag(kind: str) -> str:
    return f'{LISTING_TAG_PREFIX}{kind}'


def get_listing_kind(tags) -> str | None:
    for tag in tags or []:
        if isinstance(tag, str) and tag.startswith(LISTING_TAG_PREFIX):
            return tag[len(LISTING_TAG_PREFIX):]
    return None


def with_listing_kind(tags, kind: str | None):
    cleaned = [
        tag
        for tag in (tags or [])
        if not (isinstance(tag, str) and tag.startswith(LISTING_TAG_PREFIX))
    ]
    if kind:
        cleaned.append(listing_tag(kind))
    return cleaned


def filter_queryset_by_listing_kind(queryset, kind: str | None):
    """Filter tasks that carry a listing:* tag."""
    if kind not in LISTING_KIND_CHOICES:
        return queryset

    tag = listing_tag(kind)
    if connection.features.supports_json_field_contains:
        return queryset.filter(tags__contains=[tag])

    # SQLite (dev) lacks JSON contains; match the quoted array element in JSON text.
    return queryset.filter(tags__icontains=f'"{tag}"')


def filter_queryset_plain_tasks(queryset):
    """Exclude service/project/job dashboard listings — keep marketplace tasks only."""
    for kind in LISTING_KIND_CHOICES:
        tag = listing_tag(kind)
        if connection.features.supports_json_field_contains:
            queryset = queryset.exclude(tags__contains=[tag])
        else:
            queryset = queryset.exclude(tags__icontains=f'"{tag}"')
    return queryset
