"""Job-facing serializers (backed by Task rows tagged listing:job)."""
from rest_framework import serializers

from apps.tasks.serializers import (
    TaskCreateSerializer,
    TaskDetailSerializer,
    TaskListSerializer,
    TaskUpdateSerializer,
)
from .meta import parse_job_meta


class JobListSerializer(TaskListSerializer):
    job_meta = serializers.SerializerMethodField()

    class Meta(TaskListSerializer.Meta):
        fields = [*TaskListSerializer.Meta.fields, 'job_meta']

    def get_job_meta(self, obj):
        return parse_job_meta(obj)


class JobDetailSerializer(TaskDetailSerializer):
    job_meta = serializers.SerializerMethodField()

    class Meta(TaskDetailSerializer.Meta):
        fields = [*TaskDetailSerializer.Meta.fields, 'job_meta']

    def get_job_meta(self, obj):
        return parse_job_meta(obj)


class JobCreateSerializer(TaskCreateSerializer):
    """Create a job listing (listing_kind is always job)."""

    def validate(self, attrs):
        attrs['listing_kind'] = 'job'
        return super().validate(attrs)


class JobUpdateSerializer(TaskUpdateSerializer):
    """Update a job listing without changing listing tags."""

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if 'tags' in attrs:
            from apps.tasks.listing import get_listing_kind, with_listing_kind

            kind = get_listing_kind(self.instance.tags) or 'job'
            attrs['tags'] = with_listing_kind(attrs['tags'], kind)
        return attrs
