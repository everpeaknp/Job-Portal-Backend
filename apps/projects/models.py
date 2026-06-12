"""Project listings — proxy over Task rows tagged listing:project."""
from django.db import connection, models

from apps.tasks.listing import (
    LISTING_KIND_PROJECT,
    filter_queryset_by_listing_kind,
    listing_tag,
    with_listing_kind,
)
from apps.bids.models import Bid as BidRecord
from apps.tasks.models import Task, TaskQuestion


class ProjectQuerySet(models.QuerySet):
    def projects(self):
        return filter_queryset_by_listing_kind(self, LISTING_KIND_PROJECT)


class ProjectManager(models.Manager.from_queryset(ProjectQuerySet)):
    def get_queryset(self):
        return filter_queryset_by_listing_kind(super().get_queryset(), LISTING_KIND_PROJECT)


class Project(Task):
    """
    Employer project listing.

    Stored in the tasks table; distinguished by the listing:project tag.
    """

    objects = ProjectManager()

    class Meta:
        proxy = True
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def save(self, *args, **kwargs):
        self.tags = with_listing_kind(self.tags, LISTING_KIND_PROJECT)
        super().save(*args, **kwargs)


class ProjectQuestionQuerySet(models.QuerySet):
    def for_projects(self):
        tag = listing_tag(LISTING_KIND_PROJECT)
        if connection.features.supports_json_field_contains:
            return self.filter(task__tags__contains=[tag])
        return self.filter(task__tags__icontains=f'"{tag}"')


class ProjectQuestionManager(models.Manager.from_queryset(ProjectQuestionQuerySet)):
    def get_queryset(self):
        return super().get_queryset().for_projects()


class ProjectQuestion(TaskQuestion):
    """Questions on project listings (tasks tagged listing:project)."""

    objects = ProjectQuestionManager()

    class Meta:
        proxy = True
        verbose_name = 'Project question'
        verbose_name_plural = 'Project questions'


class ProjectBidQuerySet(models.QuerySet):
    def for_projects(self):
        tag = listing_tag(LISTING_KIND_PROJECT)
        if connection.features.supports_json_field_contains:
            return self.filter(task__tags__contains=[tag])
        return self.filter(task__tags__icontains=f'"{tag}"')


class ProjectBidManager(models.Manager.from_queryset(ProjectBidQuerySet)):
    def get_queryset(self):
        return super().get_queryset().for_projects()


class Bid(BidRecord):
    """Bids on project listings (tasks tagged listing:project)."""

    objects = ProjectBidManager()

    class Meta:
        proxy = True
        verbose_name = 'Bid'
        verbose_name_plural = 'Bids'
