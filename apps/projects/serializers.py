"""Project-facing serializers (backed by Task rows tagged listing:project)."""
from rest_framework import serializers

from apps.tasks.serializers import (
    TaskCreateSerializer,
    TaskDetailSerializer,
    TaskListSerializer,
    TaskUpdateSerializer,
)
from .meta import parse_project_meta


class ProjectListSerializer(TaskListSerializer):
    project_meta = serializers.SerializerMethodField()

    class Meta(TaskListSerializer.Meta):
        fields = [*TaskListSerializer.Meta.fields, 'project_meta']

    def get_project_meta(self, obj):
        return parse_project_meta(obj)


class ProjectDetailSerializer(TaskDetailSerializer):
    project_meta = serializers.SerializerMethodField()

    class Meta(TaskDetailSerializer.Meta):
        fields = [*TaskDetailSerializer.Meta.fields, 'project_meta']

    def get_project_meta(self, obj):
        return parse_project_meta(obj)


class ProjectCreateSerializer(TaskCreateSerializer):
    """Create a project listing (listing_kind is always project)."""

    def validate(self, attrs):
        attrs['listing_kind'] = 'project'
        return super().validate(attrs)


class ProjectUpdateSerializer(TaskUpdateSerializer):
    """Update a project listing without changing listing tags."""

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if 'tags' in attrs:
            from apps.tasks.listing import get_listing_kind, with_listing_kind

            kind = get_listing_kind(self.instance.tags) or 'project'
            attrs['tags'] = with_listing_kind(attrs['tags'], kind)
        return attrs
