import uuid

from django.db import models


class FaqItem(models.Model):
    """Platform FAQ entries managed in Django admin."""

    CATEGORY_GENERAL = 'general'
    CATEGORY_SERVICES = 'services'

    CATEGORY_CHOICES = [
        (CATEGORY_GENERAL, 'General'),
        (CATEGORY_SERVICES, 'Services'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_GENERAL,
        db_index=True,
    )
    is_published = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'question']
        verbose_name = 'FAQ item'
        verbose_name_plural = 'FAQ items'
        indexes = [
            models.Index(fields=['category', 'is_published', 'sort_order']),
        ]

    def __str__(self):
        return self.question
