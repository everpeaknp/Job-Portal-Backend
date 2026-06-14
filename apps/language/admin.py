"""Unified languages admin at /admin/language/locale/."""

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import Locale


class LocaleAdminForm(forms.ModelForm):
    class Meta:
        model = Locale
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        name = (cleaned.get('name') or '').strip()
        slug = (cleaned.get('slug') or '').strip()

        if name and not slug:
            cleaned['slug'] = slugify(name)[:100]

        if name:
            qs = Locale.objects.filter(name__iexact=name)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(f'A language named "{name}" already exists.')

        return cleaned


@admin.register(Locale)
class LocaleAdmin(admin.ModelAdmin):
    """Languages for profiles, projects, and services."""

    form = LocaleAdminForm
    list_display = ['name', 'slug', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'slug',
                'is_active',
                'order',
            ),
        }),
    )

    def get_changeform_initial_data(self, request):
        return {
            'is_active': True,
            'order': 0,
        }

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.name)[:100]
        super().save_model(request, obj, form, change)
