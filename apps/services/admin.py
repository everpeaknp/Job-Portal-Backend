"""Django admin for marketplace services (/admin/services/)."""
import json

from django.contrib import admin
from django.utils.html import format_html

from apps.tasks.admin import TaskAttachmentInline, TaskQuestionInline
from apps.tasks.listing import LISTING_KIND_SERVICE, with_listing_kind

from .meta import parse_service_meta
from .models import Service
from .service_image_seed import seed_service_cover_images


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'owner',
        'status',
        'budget_amount',
        'category',
        'city',
        'views_count',
        'created_at',
    ]
    list_filter = [
        'status',
        'work_type',
        'location_type',
        'is_public',
        'is_featured',
        'created_at',
    ]
    search_fields = ['title', 'description', 'owner__email', 'city', 'slug']
    readonly_fields = [
        'slug',
        'views_count',
        'bids_count',
        'bookmarks_count',
        'service_meta_preview',
        'created_at',
        'updated_at',
        'published_at',
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    inlines = [TaskAttachmentInline, TaskQuestionInline]

    fieldsets = (
        ('Service', {
            'fields': ('title', 'slug', 'description', 'category', 'owner'),
        }),
        ('Pricing', {
            'fields': ('budget_type', 'budget_amount', 'budget_currency'),
        }),
        ('Delivery & location', {
            'fields': (
                'work_type',
                'location_type',
                'address',
                'city',
                'state',
                'country',
                'postal_code',
                'latitude',
                'longitude',
            ),
        }),
        ('Status', {
            'fields': ('status', 'assigned_tasker', 'due_date'),
        }),
        ('Visibility', {
            'fields': ('is_public', 'is_featured', 'allow_bids'),
        }),
        ('Service metadata', {
            'fields': ('requirements', 'service_meta_preview', 'tags'),
            'description': (
                'Skills, languages, packages, and delivery times are stored in '
                'requirements as dashboard_meta JSON.'
            ),
        }),
        ('Statistics', {
            'fields': ('views_count', 'bids_count', 'bookmarks_count'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
        }),
    )

    actions = [
        'publish_services',
        'feature_services',
        'unfeature_services',
        'seed_random_images',
    ]

    @admin.display(description='Service meta')
    def service_meta_preview(self, obj):
        meta = parse_service_meta(obj)
        if not meta:
            return '—'
        text = json.dumps(meta, indent=2, ensure_ascii=False)
        return format_html('<pre style="max-width:640px;white-space:pre-wrap;">{}</pre>', text)

    def save_model(self, request, obj, form, change):
        obj.tags = with_listing_kind(obj.tags, LISTING_KIND_SERVICE)
        super().save_model(request, obj, form, change)

    @admin.action(description='Publish selected draft services')
    def publish_services(self, request, queryset):
        count = 0
        for service in queryset.filter(status='draft'):
            service.publish()
            count += 1
        self.message_user(request, f'{count} service(s) published.')

    @admin.action(description='Feature selected services')
    def feature_services(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} service(s) featured.')

    @admin.action(description='Unfeature selected services')
    def unfeature_services(self, request, queryset):
        count = queryset.update(is_featured=False)
        self.message_user(request, f'{count} service(s) unfeatured.')

    @admin.action(description='Seed random cover images (skips services that already have one)')
    def seed_random_images(self, request, queryset):
        created, skipped = seed_service_cover_images(
            queryset.select_related('owner').prefetch_related('attachments'),
            only_missing=True,
        )
        self.message_user(
            request,
            f'{created} cover image(s) added. {skipped} service(s) skipped (already had images or invalid).',
        )
