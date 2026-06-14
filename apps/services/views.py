"""Dedicated marketplace services API (Task rows with listing:service tag)."""
from django.db.models import Q
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Service
from apps.tasks.permissions import IsTaskOwner
from apps.bookmark.mixins import BookmarkSerializerContextMixin
from .permissions import CanCreateService
from .serializers import (
    ServiceCreateSerializer,
    ServiceDetailSerializer,
    ServiceListSerializer,
    ServiceUpdateSerializer,
)


class ServiceViewSet(BookmarkSerializerContextMixin, viewsets.ModelViewSet):
    """
    Marketplace services API.

    GET  /api/v1/services/           — public open services
    GET  /api/v1/services/{slug}/    — service detail
    POST /api/v1/services/           — create (taskers)
    PATCH /api/v1/services/{slug}/   — update (owner)
    DELETE /api/v1/services/{slug}/  — delete (owner)
    GET  /api/v1/services/mine/      — current user's services
    """

    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'city', 'tags']
    ordering_fields = ['created_at', 'budget_amount', 'bids_count', 'views_count']
    filterset_fields = ['status', 'category', 'work_type', 'location_type', 'city', 'country']

    def get_queryset(self):
        user = self.request.user
        queryset = Service.objects.all()

        if user.is_authenticated:
            queryset = queryset.filter(Q(is_public=True) | Q(owner=user))
        else:
            queryset = queryset.filter(is_public=True, status='open')

        return queryset.select_related(
            'owner', 'category', 'assigned_tasker'
        ).prefetch_related('attachments')

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if self.action == 'list' and not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public=True, status='open')
        return queryset

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'mine':
            return ServiceListSerializer
        if self.action == 'retrieve':
            return ServiceDetailSerializer
        if self.action == 'create':
            return ServiceCreateSerializer
        if self.action in ('update', 'partial_update'):
            return ServiceUpdateSerializer
        return ServiceDetailSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), CanCreateService()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsTaskOwner()]
        if self.action == 'mine':
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        output = ServiceDetailSerializer(task, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        output = ServiceDetailSerializer(task, context={'request': request})
        return Response(output.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['get', 'post'], url_path='reviews')
    def reviews(self, request, slug=None):
        """
        GET  /api/v1/services/{slug}/reviews/ — public reviews on this service listing.
        POST /api/v1/services/{slug}/reviews/ — authenticated users may review without a completed order.
        """
        from apps.reviews.serializers import (
            ReviewDetailSerializer,
            ReviewListSerializer,
            ServiceReviewCreateSerializer,
        )
        from apps.reviews.services import ReviewService

        service = self.get_object()

        if request.method == 'POST':
            if not request.user.is_authenticated:
                return Response(
                    {'detail': 'Authentication credentials were not provided.'},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            serializer = ServiceReviewCreateSerializer(
                data=request.data,
                context={'request': request, 'service': service},
            )
            serializer.is_valid(raise_exception=True)
            review = serializer.save()
            return Response(
                ReviewDetailSerializer(review, context={'request': request}).data,
                status=status.HTTP_201_CREATED,
            )

        qs = ReviewService.service_page_reviews_queryset(service).select_related(
            'reviewer', 'reviewee',
        ).prefetch_related('helpful_votes', 'reports')
        return Response({
            'task_id': str(service.id),
            'count': qs.count(),
            'results': ReviewListSerializer(qs, many=True, context={'request': request}).data,
        })

    @action(detail=False, methods=['get'], url_path='mine')
    def mine(self, request):
        """Dashboard: services owned by the authenticated user."""
        queryset = (
            Service.objects.filter(owner=request.user)
            .select_related('owner', 'category')
            .prefetch_related('attachments')
            .order_by('-created_at')
        )
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ServiceListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ServiceListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
