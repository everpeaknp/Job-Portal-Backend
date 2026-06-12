"""Django admin for marketplace projects (/admin/projects/)."""
import json

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from apps.tasks.admin import TaskAttachmentInline, TaskQuestionInline
from apps.tasks.listing import LISTING_KIND_PROJECT, with_listing_kind

from .meta import parse_project_meta
from .models import Bid, Project, ProjectQuestion


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'owner',
        'status',
        'budget_amount',
        'category',
        'city',
        'bids_count',
        'created_at',
    ]
    list_filter = [
        'status',
        'work_type',
        'location_type',
        'is_public',
        'created_at',
    ]
    search_fields = ['title', 'description', 'owner__email', 'city', 'slug']
    readonly_fields = [
        'slug',
        'views_count',
        'bids_count',
        'bookmarks_count',
        'project_meta_preview',
        'created_at',
        'updated_at',
        'published_at',
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    inlines = [TaskAttachmentInline, TaskQuestionInline]

    fieldsets = (
        ('Project', {
            'fields': ('title', 'slug', 'description', 'category', 'owner'),
        }),
        ('Budget', {
            'fields': ('budget_type', 'budget_amount', 'budget_currency'),
        }),
        ('Location', {
            'fields': (
                'work_type',
                'location_type',
                'address',
                'city',
                'state',
                'country',
                'latitude',
                'longitude',
            ),
        }),
        ('Status', {
            'fields': ('status', 'assigned_tasker', 'due_date'),
        }),
        ('Visibility', {
            'fields': ('is_public', 'allow_bids'),
        }),
        ('Project metadata', {
            'fields': ('requirements', 'project_meta_preview', 'tags'),
        }),
        ('Statistics', {
            'fields': ('views_count', 'bids_count', 'bookmarks_count'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
        }),
    )

    @admin.display(description='Project meta')
    def project_meta_preview(self, obj):
        meta = parse_project_meta(obj)
        if not meta:
            return '—'
        text = json.dumps(meta, indent=2, ensure_ascii=False)
        return format_html('<pre style="max-width:640px;white-space:pre-wrap;">{}</pre>', text)

    def save_model(self, request, obj, form, change):
        obj.tags = with_listing_kind(obj.tags, LISTING_KIND_PROJECT)
        super().save_model(request, obj, form, change)


@admin.register(ProjectQuestion)
class ProjectQuestionAdmin(admin.ModelAdmin):
    """Admin for questions on project listings (/admin/projects/projectquestion/)."""

    list_display = ['task', 'asked_by', 'is_answered', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['task__title', 'asked_by__email', 'question', 'answer']
    readonly_fields = ['created_at', 'answered_at']
    ordering = ['-created_at']
    autocomplete_fields = ['task', 'asked_by']

    fieldsets = (
        (None, {
            'fields': ('task', 'asked_by', 'question', 'answer'),
        }),
        ('Settings', {
            'fields': ('is_public', 'created_at', 'answered_at'),
        }),
    )

    def get_queryset(self, request):
        return ProjectQuestion.objects.all()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'task':
            kwargs['queryset'] = Project.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Bid)
class ProjectBidAdmin(admin.ModelAdmin):
    """Bids on project listings (/admin/projects/bid/)."""

    list_display = [
        'id',
        'project_link',
        'tasker_link',
        'amount_display',
        'status_badge',
        'created_at',
        'is_counter_offer',
    ]
    list_filter = ['status', 'is_counter_offer', 'created_at', 'currency']
    search_fields = [
        'task__title',
        'tasker__email',
        'tasker__first_name',
        'tasker__last_name',
        'proposal',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'accepted_at',
        'rejected_at',
        'withdrawn_at',
    ]
    date_hierarchy = 'created_at'
    autocomplete_fields = ['task', 'tasker']

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'task', 'tasker', 'status'),
        }),
        ('Offer Details', {
            'fields': (
                'amount',
                'currency',
                'proposal',
                'cover_letter',
                'estimated_duration',
                'estimated_completion_date',
                'attachments',
            ),
        }),
        ('Counter Offer', {
            'fields': ('is_counter_offer', 'original_bid'),
            'classes': ('collapse',),
        }),
        ('Status Details', {
            'fields': ('rejection_reason', 'withdrawal_reason'),
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'accepted_at',
                'rejected_at',
                'withdrawn_at',
            ),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return Bid.objects.select_related('task', 'tasker', 'original_bid').all()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'task':
            kwargs['queryset'] = Project.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description='Project')
    def project_link(self, obj):
        url = reverse('admin:projects_project_change', args=[obj.task.id])
        return format_html('<a href="{}">{}</a>', url, obj.task.title[:50])

    @admin.display(description='Tasker')
    def tasker_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.tasker.id])
        return format_html('<a href="{}">{}</a>', url, obj.tasker.get_full_name())

    @admin.display(description='Amount')
    def amount_display(self, obj):
        return f'{obj.currency} {obj.amount}'

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'accepted': '#28A745',
            'rejected': '#DC3545',
            'withdrawn': '#6C757D',
            'expired': '#6C757D',
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.status.upper(),
        )
