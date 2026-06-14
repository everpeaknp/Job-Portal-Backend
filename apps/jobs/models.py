"""Job listings — proxy over Task rows tagged listing:job."""

from django.db import connection, models

from apps.bids.models import Bid as BidRecord
from apps.tasks.listing import (
    LISTING_KIND_JOB,
    filter_queryset_by_listing_kind,
    listing_tag,
    with_listing_kind,
)
from apps.tasks.models import Task, TaskQuestion


class JobQuerySet(models.QuerySet):
    def jobs(self):
        return filter_queryset_by_listing_kind(self, LISTING_KIND_JOB)


class JobManager(models.Manager.from_queryset(JobQuerySet)):
    def get_queryset(self):
        return filter_queryset_by_listing_kind(super().get_queryset(), LISTING_KIND_JOB)


class Job(Task):
    """Employer job listing stored in tasks table with listing:job tag."""

    objects = JobManager()

    class Meta:
        proxy = True
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'

    def save(self, *args, **kwargs):
        self.tags = with_listing_kind(self.tags, LISTING_KIND_JOB)
        super().save(*args, **kwargs)


class JobQuestionQuerySet(models.QuerySet):
    def for_jobs(self):
        tag = listing_tag(LISTING_KIND_JOB)
        if connection.features.supports_json_field_contains:
            return self.filter(task__tags__contains=[tag])
        return self.filter(task__tags__icontains=f'"{tag}"')


class JobQuestionManager(models.Manager.from_queryset(JobQuestionQuerySet)):
    def get_queryset(self):
        return super().get_queryset().for_jobs()


class JobQuestion(TaskQuestion):
    """Questions on job listings."""

    objects = JobQuestionManager()

    class Meta:
        proxy = True
        verbose_name = 'Job question'
        verbose_name_plural = 'Job questions'


class JobBidQuerySet(models.QuerySet):
    def for_jobs(self):
        tag = listing_tag(LISTING_KIND_JOB)
        if connection.features.supports_json_field_contains:
            return self.filter(task__tags__contains=[tag])
        return self.filter(task__tags__icontains=f'"{tag}"')


class JobBidManager(models.Manager.from_queryset(JobBidQuerySet)):
    def get_queryset(self):
        return super().get_queryset().for_jobs()


class Bid(BidRecord):
    """Bids on job listings."""

    objects = JobBidManager()

    class Meta:
        proxy = True
        verbose_name = 'Bid'
        verbose_name_plural = 'Bids'
