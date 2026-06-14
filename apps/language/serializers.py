from rest_framework import serializers

from .models import Locale


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locale
        fields = [
            'id',
            'name',
            'slug',
            'is_active',
            'order',
        ]
        read_only_fields = fields
