from django import forms
from django.contrib import admin

from .models import FaqItem


class FaqItemAdminForm(forms.ModelForm):
    class Meta:
        model = FaqItem
        fields = '__all__'
        widgets = {
            'answer': forms.Textarea(attrs={'rows': 5}),
        }


@admin.register(FaqItem)
class FaqItemAdmin(admin.ModelAdmin):
    form = FaqItemAdminForm
    list_display = ('question', 'category', 'is_published', 'sort_order', 'updated_at')
    list_filter = ('category', 'is_published')
    search_fields = ('question', 'answer')
    ordering = ('sort_order', 'question')
    readonly_fields = ('created_at', 'updated_at')
