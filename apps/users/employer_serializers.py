"""Serializers for employer business profiles."""
from rest_framework import serializers

from .employer_profile_service import resolve_employer_image_url
from .models import EmployerGalleryImage, EmployerProfile, User


class EmployerGalleryImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = EmployerGalleryImage
        fields = ['id', 'url', 'alt_text', 'sort_order', 'created_at']
        read_only_fields = fields

    def get_url(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        return resolve_employer_image_url(request, obj.image)


class EmployerProfileWriteSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(source='user.username', required=False, allow_blank=True)
    tagline = serializers.CharField(source='user.tagline', required=False, allow_blank=True)
    description = serializers.CharField(source='user.bio', required=False, allow_blank=True)
    location = serializers.CharField(source='user.city', required=False, allow_blank=True)
    logo_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EmployerProfile
        fields = [
            'account_type',
            'company_name',
            'industry',
            'team_size',
            'website',
            'cost_range',
            'contact_email',
            'contact_phone',
            'logo_color',
            'logo_text',
            'is_public',
            'slug',
            'tagline',
            'description',
            'location',
            'logo_url',
            'updated_at',
        ]
        read_only_fields = ['logo_url', 'updated_at']

    def get_logo_url(self, obj):
        request = self.context.get('request')
        logo = resolve_employer_image_url(request, obj.logo_image) if request else None
        if logo:
            return logo
        if request and obj.user.profile_image:
            return resolve_employer_image_url(request, obj.user.profile_image)
        return None

    def validate_slug(self, value):
        from .username_policy import assert_username_change_allowed, normalize_username

        normalized = normalize_username(value)
        user = self.context['request'].user
        if user.username and user.username.lower() != normalized:
            assert_username_change_allowed(user, normalized)
        if User.objects.filter(username__iexact=normalized).exclude(pk=user.pk).exists():
            raise serializers.ValidationError('This profile URL is already taken.')
        return normalized

    def update(self, instance, validated_data):
        from django.utils import timezone

        from .username_policy import normalize_username, usernames_equal

        user_data = validated_data.pop('user', {})
        user = instance.user

        new_username = user_data.get('username')
        if new_username is not None:
            normalized = normalize_username(new_username)
            if not usernames_equal(user.username, normalized):
                user.username = normalized
                user.username_changed_at = timezone.now()

        for field in ('tagline', 'bio', 'city'):
            if field in user_data:
                setattr(user, field, user_data[field] or '')

        company_name = validated_data.get('company_name')
        if company_name is not None and company_name.strip():
            parts = company_name.strip().split()
            user.first_name = parts[0]
            user.last_name = ' '.join(parts[1:])

        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class EmployerPublicProfileSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    user_id = serializers.UUIDField(source='user.id')
    slug = serializers.SerializerMethodField()
    account_type = serializers.CharField()
    name = serializers.SerializerMethodField()
    tagline = serializers.SerializerMethodField()
    industry = serializers.SerializerMethodField()
    team_size = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    website = serializers.CharField(allow_blank=True)
    cost_range = serializers.CharField(allow_blank=True)
    logo_url = serializers.SerializerMethodField()
    logo_color = serializers.CharField()
    logo_text = serializers.CharField()
    contact_email = serializers.CharField(allow_blank=True, required=False)
    contact_phone = serializers.CharField(allow_blank=True, required=False)
    gallery_images = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    review_count = serializers.IntegerField(source='user.total_reviews')
    open_jobs = serializers.SerializerMethodField()
    member_since = serializers.DateTimeField(source='user.date_joined')

    def get_id(self, obj):
        return f'emp-user-{obj.user_id}'

    def get_slug(self, obj):
        return (obj.user.username or '').lower()

    def get_name(self, obj):
        return obj.company_name.strip() or obj.user.get_full_name() or obj.user.username or 'Employer'

    def get_tagline(self, obj):
        return obj.user.tagline or ''

    def get_industry(self, obj):
        if obj.account_type == 'individual':
            return 'Individual'
        return obj.industry or 'Not specified'

    def get_team_size(self, obj):
        if obj.account_type == 'individual':
            return '—'
        return obj.team_size or 'Not specified'

    def get_location(self, obj):
        return obj.user.city or obj.user.address or 'Not specified'

    def get_description(self, obj):
        return obj.user.bio or ''

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        logo = resolve_employer_image_url(request, obj.logo_image)
        if logo:
            return logo
        return resolve_employer_image_url(request, obj.user.profile_image)

    def get_gallery_images(self, obj):
        if not obj.pk:
            return []
        images = obj.gallery_images.all()
        return EmployerGalleryImageSerializer(images, many=True, context=self.context).data

    def get_rating(self, obj):
        return float(obj.user.average_rating or 0)

    def get_open_jobs(self, obj):
        from .employer_profile_service import count_open_employer_listings

        return count_open_employer_listings(obj.user, 'job')


class EmployerMyProfileSerializer(EmployerProfileWriteSerializer):
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    gallery_images = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    review_count = serializers.IntegerField(source='user.total_reviews', read_only=True)
    open_jobs = serializers.SerializerMethodField()
    member_since = serializers.DateTimeField(source='user.date_joined', read_only=True)

    class Meta(EmployerProfileWriteSerializer.Meta):
        fields = EmployerProfileWriteSerializer.Meta.fields + [
            'user_id',
            'gallery_images',
            'rating',
            'review_count',
            'open_jobs',
            'member_since',
        ]
        read_only_fields = EmployerProfileWriteSerializer.Meta.read_only_fields + [
            'user_id',
            'gallery_images',
            'rating',
            'review_count',
            'open_jobs',
            'member_since',
        ]

    def get_gallery_images(self, obj):
        if not obj.pk:
            return []
        images = obj.gallery_images.all()
        return EmployerGalleryImageSerializer(images, many=True, context=self.context).data

    def get_rating(self, obj):
        return float(obj.user.average_rating or 0)

    def get_open_jobs(self, obj):
        from .employer_profile_service import count_open_employer_listings

        return count_open_employer_listings(obj.user, 'job')
