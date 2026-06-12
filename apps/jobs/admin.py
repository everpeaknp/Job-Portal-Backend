from django.contrib import admin



from .models import Job





@admin.register(Job)

class JobAdmin(admin.ModelAdmin):

    list_display = ('title', 'owner', 'status', 'is_public', 'created_at')

    search_fields = ('title', 'slug', 'owner__email')

    list_filter = ('status', 'is_public')

