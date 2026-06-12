"""Employer profile API — dashboard editing and public pages."""
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project
from apps.projects.serializers import ProjectListSerializer
from apps.jobs.models import Job
from apps.jobs.serializers import JobListSerializer
from apps.reviews.serializers import ReviewListSerializer, UserReviewStatsSerializer
from apps.reviews.services import ReviewService

from .employer_profile_service import (
    ALLOWED_EMPLOYER_IMAGE_CONTENT_TYPES,
    MAX_EMPLOYER_GALLERY_BYTES,
    MAX_EMPLOYER_GALLERY_ITEMS,
    MAX_EMPLOYER_LOGO_BYTES,
    get_employer_user_by_slug,
    get_or_create_employer_profile,
)
from .employer_serializers import (
    EmployerGalleryImageSerializer,
    EmployerMyProfileSerializer,
    EmployerProfileWriteSerializer,
    EmployerPublicProfileSerializer,
)
from .models import EmployerGalleryImage, EmployerProfile


class EmployerProfileMeView(APIView):
    """GET/PATCH /api/v1/users/me/employer-profile/"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'customer':
            return Response(
                {'error': 'Only employer accounts can manage a business profile.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        profile = get_or_create_employer_profile(request.user)
        profile = (
            EmployerProfile.objects.filter(pk=profile.pk)
            .select_related('user')
            .prefetch_related('gallery_images')
            .first()
        )
        serializer = EmployerMyProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        if request.user.role != 'customer':
            return Response(
                {'error': 'Only employer accounts can manage a business profile.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        profile = get_or_create_employer_profile(request.user)
        serializer = EmployerProfileWriteSerializer(
            profile,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        profile = (
            EmployerProfile.objects.filter(pk=profile.pk)
            .select_related('user')
            .prefetch_related('gallery_images')
            .first()
        )
        output = EmployerMyProfileSerializer(profile, context={'request': request})
        return Response(output.data)


class EmployerLogoUploadView(APIView):
    """POST /api/v1/users/me/employer-profile/logo/"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'customer':
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        uploaded = request.FILES.get('file') or request.FILES.get('logo')
        if not uploaded:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        if uploaded.size > MAX_EMPLOYER_LOGO_BYTES:
            return Response({'error': 'Logo must be 1MB or smaller.'}, status=status.HTTP_400_BAD_REQUEST)
        content_type = (uploaded.content_type or '').lower()
        if content_type and content_type not in ALLOWED_EMPLOYER_IMAGE_CONTENT_TYPES:
            return Response(
                {'error': 'Logo must be JPG, PNG, or WEBP.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = get_or_create_employer_profile(request.user)
        if profile.logo_image:
            profile.logo_image.delete(save=False)
        profile.logo_image = uploaded
        profile.save(update_fields=['logo_image', 'updated_at'])

        output = EmployerMyProfileSerializer(profile, context={'request': request})
        return Response(output.data, status=status.HTTP_200_OK)


class EmployerGalleryListCreateView(APIView):
    """GET/POST /api/v1/users/me/employer-profile/gallery/"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_or_create_employer_profile(request.user)
        images = profile.gallery_images.all()
        serializer = EmployerGalleryImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'customer':
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        profile = get_or_create_employer_profile(request.user)
        if profile.gallery_images.count() >= MAX_EMPLOYER_GALLERY_ITEMS:
            return Response(
                {'error': f'Maximum {MAX_EMPLOYER_GALLERY_ITEMS} gallery images allowed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        uploaded = request.FILES.get('file') or request.FILES.get('image')
        if not uploaded:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        if uploaded.size > MAX_EMPLOYER_GALLERY_BYTES:
            return Response(
                {'error': 'Each gallery image must be 1MB or smaller.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        content_type = (uploaded.content_type or '').lower()
        if content_type and content_type not in ALLOWED_EMPLOYER_IMAGE_CONTENT_TYPES:
            return Response(
                {'error': 'Gallery images must be JPG, PNG, or WEBP.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        alt_text = (request.data.get('alt_text') or request.data.get('alt') or '').strip()[:255]
        sort_order = profile.gallery_images.count()
        image = EmployerGalleryImage.objects.create(
            profile=profile,
            image=uploaded,
            alt_text=alt_text,
            sort_order=sort_order,
        )
        serializer = EmployerGalleryImageSerializer(image, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EmployerGalleryDetailView(APIView):
    """DELETE /api/v1/users/me/employer-profile/gallery/<uuid:id>/"""

    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        profile = get_or_create_employer_profile(request.user)
        image = get_object_or_404(EmployerGalleryImage, pk=id, profile=profile)
        image.image.delete(save=False)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmployerPublicDetailView(APIView):
    """GET /api/v1/employers/<slug>/"""

    permission_classes = [AllowAny]

    def get(self, request, slug):
        user = get_employer_user_by_slug(slug)
        if not user:
            return Response({'error': 'Employer not found.'}, status=status.HTTP_404_NOT_FOUND)

        profile = EmployerProfile.objects.filter(user=user).prefetch_related('gallery_images').first()
        if not profile:
            profile = get_or_create_employer_profile(user)
        elif not profile.is_public and request.user != user:
            return Response({'error': 'Employer not found.'}, status=status.HTTP_404_NOT_FOUND)

        if profile.pk:
            profile = (
                EmployerProfile.objects.filter(pk=profile.pk)
                .select_related('user')
                .prefetch_related('gallery_images')
                .first()
            )
        serializer = EmployerPublicProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)


class EmployerPublicProjectsView(APIView):
    """GET /api/v1/employers/<slug>/projects/"""

    permission_classes = [AllowAny]

    def get(self, request, slug):
        user = get_employer_user_by_slug(slug)
        if not user:
            return Response({'error': 'Employer not found.'}, status=status.HTTP_404_NOT_FOUND)

        queryset = (
            Project.objects.filter(owner=user, is_public=True, status='open')
            .select_related('owner', 'owner__employer_profile', 'category')
            .order_by('-created_at')
        )
        serializer = ProjectListSerializer(queryset, many=True, context={'request': request})
        return Response({'count': queryset.count(), 'results': serializer.data})


class EmployerPublicJobsView(APIView):
    """GET /api/v1/employers/<slug>/jobs/"""

    permission_classes = [AllowAny]

    def get(self, request, slug):
        user = get_employer_user_by_slug(slug)
        if not user:
            return Response({'error': 'Employer not found.'}, status=status.HTTP_404_NOT_FOUND)

        queryset = (
            Job.objects.filter(owner=user, is_public=True, status='open')
            .select_related('owner', 'owner__employer_profile', 'category')
            .order_by('-created_at')
        )
        serializer = JobListSerializer(queryset, many=True, context={'request': request})
        return Response({'count': queryset.count(), 'results': serializer.data})


class EmployerPublicReviewsView(APIView):
    """GET /api/v1/employers/<slug>/reviews/"""

    permission_classes = [AllowAny]

    def get(self, request, slug):
        user = get_employer_user_by_slug(slug)
        if not user:
            return Response({'error': 'Employer not found.'}, status=status.HTTP_404_NOT_FOUND)

        reviews = ReviewService.get_reviews_received(user)
        stats = ReviewService.get_review_statistics(user)
        data = ReviewListSerializer(reviews, many=True, context={'request': request}).data
        return Response({
            'user_id': str(user.id),
            'statistics': UserReviewStatsSerializer(stats).data,
            'count': reviews.count(),
            'results': data,
        })
