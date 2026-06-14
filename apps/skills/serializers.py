from rest_framework import serializers

from .models import Skill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = [
            'id',
            'name',
            'slug',
            'listing_kind',
            'description',
            'is_active',
            'order',
        ]
        read_only_fields = fields
