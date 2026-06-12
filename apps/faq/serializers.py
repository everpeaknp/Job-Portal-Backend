from rest_framework import serializers

from .models import FaqItem


class FaqItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaqItem
        fields = ['id', 'question', 'answer', 'category', 'sort_order']
