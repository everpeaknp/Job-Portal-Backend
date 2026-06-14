"""Unified marketplace categories (task, job, project, service)."""

from django.db import models

from apps.tasks.models import Category as BaseCategory


class Category(BaseCategory):
    """All listing categories — managed at /admin/category/category/."""

    class Meta:
        proxy = True
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
