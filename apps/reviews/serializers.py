"""Serializers for bidirectional reviews."""
from rest_framework import serializers

from apps.tasks.listing import get_listing_kind
from apps.tasks.serializers import TaskListSerializer
from apps.users.serializers import PublicUserSerializer

from .models import Review, ReviewHelpful, ReviewReport, ReviewInvitation
from .services import ReviewService


class ReviewListSerializer(serializers.ModelSerializer):
    reviewer = PublicUserSerializer(read_only=True)
    reviewee = PublicUserSerializer(read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    task_budget_type = serializers.CharField(source='task.budget_type', read_only=True)
    task_listing_kind = serializers.SerializerMethodField()
    rating = serializers.IntegerField(source='overall_rating', read_only=True)
    comment = serializers.CharField(source='review_text', read_only=True)
    helpful_count = serializers.SerializerMethodField()
    not_helpful_count = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    is_reported = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id',
            'task',
            'task_title',
            'task_budget_type',
            'task_listing_kind',
            'reviewer',
            'reviewee',
            'reviewer_type',
            'review_type',
            'rating',
            'comment',
            'tags',
            'would_recommend',
            'is_verified',
            'response_text',
            'response_at',
            'created_at',
            'helpful_count',
            'not_helpful_count',
            'user_vote',
            'is_reported',
        ]
        read_only_fields = fields

    def get_task_listing_kind(self, obj):
        return get_listing_kind(getattr(obj.task, 'tags', None))

    def _vote_counts(self, obj):
        cached = getattr(obj, '_helpful_counts', None)
        if cached is not None:
            return cached
        helpful = 0
        not_helpful = 0
        for vote in obj.helpful_votes.all():
            if vote.is_helpful:
                helpful += 1
            else:
                not_helpful += 1
        return helpful, not_helpful

    def get_helpful_count(self, obj):
        return self._vote_counts(obj)[0]

    def get_not_helpful_count(self, obj):
        return self._vote_counts(obj)[1]

    def get_user_vote(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        vote = obj.helpful_votes.filter(user=request.user).first()
        if not vote:
            return None
        return 'helpful' if vote.is_helpful else 'not_helpful'

    def get_is_reported(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.reports.filter(reporter=request.user).exists()


class ReviewDetailSerializer(ReviewListSerializer):
    task = TaskListSerializer(read_only=True)

    class Meta(ReviewListSerializer.Meta):
        fields = ReviewListSerializer.Meta.fields + [
            'communication_rating',
            'quality_rating',
            'speed_rating',
            'professionalism_rating',
            'clarity_rating',
            'payment_experience_rating',
            'would_work_again',
            'is_public',
            'visible_at',
            'updated_at',
        ]


class ServiceReviewCreateSerializer(serializers.Serializer):
    """POST /api/v1/services/{slug}/reviews/ — open review on a service listing."""

    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=5000)

    def create(self, validated_data):
        request = self.context['request']
        service = self.context['service']
        return ReviewService.create_service_listing_review(
            service=service,
            reviewer=request.user,
            rating=validated_data['rating'],
            comment=validated_data.get('comment', ''),
            submitter_ip=request.META.get('REMOTE_ADDR'),
            submitter_user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )


class ReviewCreateSerializer(serializers.Serializer):
    """
    POST /api/v1/reviews/create/
    Server assigns reviewee and reviewer_type — never accept them from client.
    """

    task_id = serializers.UUIDField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=5000)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=64),
        required=False,
        allow_empty=True,
    )

    def create(self, validated_data):
        request = self.context['request']
        return ReviewService.create_review(
            task_id=validated_data['task_id'],
            reviewer=request.user,
            rating=validated_data['rating'],
            comment=validated_data.get('comment', ''),
            tags=validated_data.get('tags'),
            submitter_ip=request.META.get('REMOTE_ADDR'),
            submitter_user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )


class ReviewRespondSerializer(serializers.Serializer):
    response_text = serializers.CharField(max_length=2000)

    def validate(self, attrs):
        review = self.context['review']
        user = self.context['request'].user
        if user != review.reviewee:
            raise serializers.ValidationError('Only the reviewee can respond.')
        if review.response_text:
            raise serializers.ValidationError('This review already has a response.')
        if review.is_finalized and ReviewService.get_settings().edit_window_minutes == 0:
            pass
        return attrs

    def save(self):
        review = self.context['review']
        from django.utils import timezone

        review.response_text = self.validated_data['response_text']
        review.response_at = timezone.now()
        review.save(update_fields=['response_text', 'response_at', 'updated_at'])
        return review


class ReviewInvitationSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    reviewee_id = serializers.SerializerMethodField()

    class Meta:
        model = ReviewInvitation
        fields = [
            'id',
            'task',
            'task_title',
            'reviewer_type',
            'reviewee_id',
            'status',
            'sent_at',
            'expires_at',
            'completed_at',
            'is_expired',
        ]
        read_only_fields = fields

    def get_reviewee_id(self, obj):
        from .constants import REVIEWER_TYPE_CUSTOMER

        task = obj.task
        if obj.reviewer_type == REVIEWER_TYPE_CUSTOMER:
            return str(task.assigned_tasker_id) if task.assigned_tasker_id else None
        return str(task.owner_id)


class ReviewHelpfulVoteSerializer(serializers.Serializer):
    """POST vote: helpful | not_helpful | clear"""

    vote = serializers.ChoiceField(choices=['helpful', 'not_helpful', 'clear'])


class ReviewReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReport
        fields = ['reason', 'description']

    def validate(self, attrs):
        review = self.context['review']
        user = self.context['request'].user
        if ReviewReport.objects.filter(review=review, reporter=user).exists():
            raise serializers.ValidationError('You have already reported this review.')
        return attrs

    def create(self, validated_data):
        review = self.context['review']
        return ReviewReport.objects.create(
            review=review,
            reporter=self.context['request'].user,
            **validated_data,
        )


class UserReviewStatsSerializer(serializers.Serializer):
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField(allow_null=True)
    rating_distribution = serializers.DictField(child=serializers.IntegerField())
    as_tasker_reviews = serializers.IntegerField()
    as_customer_reviews = serializers.IntegerField()
    trust_score = serializers.FloatField()
