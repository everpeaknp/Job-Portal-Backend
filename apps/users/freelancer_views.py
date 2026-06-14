"""Freelancer (tasker) profile API — dashboard editing and public pages."""
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reviews.serializers import ReviewListSerializer, UserReviewStatsSerializer
from apps.reviews.services import ReviewService
from apps.services.models import Service
from apps.services.serializers import ServiceListSerializer

from .freelancer_profile_service import (
    freelancer_public_slug,
    get_freelancer_user_by_slug,
    is_freelancer_public_profile_ready,
)
from .models import User
from .portfolio_service import get_public_portfolio_items, portfolio_document_status_map
from .serializers import (
    PortfolioItemSerializer,
    PublicProfileSerializer,
    UserDetailSerializer,
    UserProfileSerializer,
)


def _prefetch_freelancer_user(user: User) -> User:
    return (
        User.objects.filter(pk=user.pk)
        .prefetch_related('skills', 'badges')
        .first()
        or user
    )


class FreelancerProfileMeView(APIView):
    """GET/PATCH /api/v1/users/me/freelancer-profile/"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = _prefetch_freelancer_user(request.user)
        profile = PublicProfileSerializer(user, context={'request': request}).data
        detail = UserDetailSerializer(user, context={'request': request}).data
        return Response({
            'slug': freelancer_public_slug(user),
            'profile': profile,
            **detail,
        })

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = _prefetch_freelancer_user(request.user)
        profile = PublicProfileSerializer(user, context={'request': request}).data
        detail = UserDetailSerializer(user, context={'request': request}).data
        return Response({
            'slug': freelancer_public_slug(user),
            'profile': profile,
            **detail,
        })


class FreelancerPublicDetailView(APIView):
    """GET /api/v1/freelancers/<slug>/"""

    permission_classes = [AllowAny]

    def get(self, request, slug):
        user = get_freelancer_user_by_slug(slug)
        if not user:
            return Response({'error': 'Freelancer not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = _prefetch_freelancer_user(user)
        data = PublicProfileSerializer(user, context={'request': request}).data
        data['slug'] = freelancer_public_slug(user)
        data['profile_configured'] = is_freelancer_public_profile_ready(user)
        return Response(data)


class FreelancerPublicReviewsView(APIView):
    """GET /api/v1/freelancers/<slug>/reviews/"""

    permission_classes = [AllowAny]

    def get(self, request, slug):
        user = get_freelancer_user_by_slug(slug)
        if not user:
            return Response({'error': 'Freelancer not found.'}, status=status.HTTP_404_NOT_FOUND)

        reviews = ReviewService.get_reviews_received(user)
        stats = ReviewService.get_review_statistics(user)
        data = ReviewListSerializer(reviews, many=True, context={'request': request}).data
        return Response({
            'user_id': str(user.id),
            'statistics': UserReviewStatsSerializer(stats).data,
            'count': reviews.count(),
            'results': data,
        })


class FreelancerPublicPortfolioView(APIView):
    """GET /api/v1/freelancers/<slug>/portfolio/"""

    permission_classes = [AllowAny]

    def get(self, request, slug):
        user = get_freelancer_user_by_slug(slug)
        if not user:
            return Response({'error': 'Freelancer not found.'}, status=status.HTTP_404_NOT_FOUND)

        portfolio_items = get_public_portfolio_items(user)
        doc_map = portfolio_document_status_map(user)
        serializer = PortfolioItemSerializer(
            portfolio_items,
            many=True,
            context={'request': request, 'portfolio_doc_map': doc_map},
        )
        return Response({'count': len(serializer.data), 'results': serializer.data})


class FreelancerPublicServicesView(APIView):
    """GET /api/v1/freelancers/<slug>/services/"""

    permission_classes = [AllowAny]

    def get(self, request, slug):
        user = get_freelancer_user_by_slug(slug)
        if not user:
            return Response({'error': 'Freelancer not found.'}, status=status.HTTP_404_NOT_FOUND)

        queryset = (
            Service.objects.filter(owner=user, is_public=True, status='open')
            .select_related('owner', 'category')
            .order_by('-created_at')
        )
        serializer = ServiceListSerializer(queryset, many=True, context={'request': request})
        return Response({'count': queryset.count(), 'results': serializer.data})
