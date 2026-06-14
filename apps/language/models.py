"""Marketplace language options for profiles, projects, and services."""

import uuid

from django.db import models

CANONICAL_LANGUAGES = (
    'English',
    'Nepali',
    'Hindi',
    'Maithili',
    'Bhojpuri',
    'Tharu',
    'Tamang',
    'Newari',
    'Magar',
    'Gurung',
    'Sherpa',
    'Limbu',
    'Rai',
    'Awadhi',
    'Doteli',
    'Urdu',
    'Bajjika',
    'French',
    'German',
    'Spanish',
)


class Locale(models.Model):
    """Selectable languages for freelancer profiles and listing forms."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'marketplace_languages'
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name
