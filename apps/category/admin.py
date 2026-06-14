"""Unified category admin at /admin/category/."""

from django.contrib import admin

from apps.jobs.models import Job
from apps.tasks.listing import LISTING_KIND_JOB
from apps.tasks.models import Category as TaskCategory

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """All marketplace categories in one place."""

    list_display = [
        'name',
        'slug',
        'listing_kind',
        'parent',
        'is_active',
        'order',
        'listing_count',
    ]
    list_filter = ['listing_kind', 'is_active', 'parent']
    search_fields = ['name', 'description', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['listing_kind', 'order', 'name']
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'slug',
                'listing_kind',
                'description',
                'icon',
                'parent',
                'is_active',
                'order',
            ),
        }),
    )

    def get_queryset(self, request):
        return TaskCategory.objects.all()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            kwargs['queryset'] = TaskCategory.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description='Listings')
    def listing_count(self, obj):
        if obj.listing_kind == LISTING_KIND_JOB:
            return Job.objects.filter(category_id=obj.pk).count()
        return obj.tasks.count()
