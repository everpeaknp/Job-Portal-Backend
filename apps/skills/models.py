"""Marketplace skill tags for jobs, projects, and services."""

import uuid

from django.db import models

from apps.tasks.listing import LISTING_KIND_CATEGORY_CHOICES, LISTING_KIND_JOB, LISTING_KIND_PROJECT, LISTING_KIND_SERVICE


class Skill(models.Model):
    """Selectable skills for dashboard job / project / service listings."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    listing_kind = models.CharField(
        max_length=20,
        choices=LISTING_KIND_CATEGORY_CHOICES,
        default=LISTING_KIND_PROJECT,
        db_index=True,
        help_text='Which listing type this skill applies to (job, project, or service).',
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'marketplace_skills'
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'
        ordering = ['listing_kind', 'order', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'listing_kind'],
                name='marketplace_skills_name_listing_kind_uniq',
            ),
            models.UniqueConstraint(
                fields=['slug', 'listing_kind'],
                name='marketplace_skills_slug_listing_kind_uniq',
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.listing_kind})'


# Re-export listing kinds used by admin/forms
LISTING_SKILL_KINDS = (
    LISTING_KIND_JOB,
    LISTING_KIND_PROJECT,
    LISTING_KIND_SERVICE,
)
