from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from .models import Locale
from .serializers import LanguageSerializer


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """Public language taxonomy for dashboard profiles and listings."""

    serializer_class = LanguageSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name']
    ordering_fields = ['order', 'name']
    ordering = ['order', 'name']

    def get_queryset(self):
        return Locale.objects.filter(is_active=True)
