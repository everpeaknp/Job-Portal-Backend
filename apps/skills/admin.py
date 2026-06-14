"""Unified skills admin at /admin/skills/."""

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from apps.tasks.listing import LISTING_KIND_CATEGORY_CHOICES

from .models import LISTING_SKILL_KINDS, Skill


class SkillAdminForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        label_map = dict(LISTING_KIND_CATEGORY_CHOICES)
        self.fields['listing_kind'].choices = [
            (kind, label_map.get(kind, kind)) for kind in LISTING_SKILL_KINDS
        ]
        self.fields['listing_kind'].help_text = (
            'Job = dashboard jobs, Project = dashboard projects, Service = dashboard services.'
        )

    def clean(self):
        cleaned = super().clean()
        name = (cleaned.get('name') or '').strip()
        listing_kind = cleaned.get('listing_kind')
        slug = (cleaned.get('slug') or '').strip()

        if name and not slug:
            cleaned['slug'] = slugify(name)[:100]

        if name and listing_kind:
            qs = Skill.objects.filter(name__iexact=name, listing_kind=listing_kind)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    f'A skill named "{name}" already exists for listing type "{listing_kind}".'
                )

        return cleaned


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Skills for jobs, projects, and services."""

    form = SkillAdminForm
    list_display = ['name', 'slug', 'listing_kind', 'is_active', 'order']
    list_filter = ['listing_kind', 'is_active']
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
                'is_active',
                'order',
            ),
        }),
    )

    def get_changeform_initial_data(self, request):
        return {
            'listing_kind': 'project',
            'is_active': True,
            'order': 0,
        }

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.name)[:100]
        super().save_model(request, obj, form, change)
