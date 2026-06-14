"""KYC (Identity Trust Program) helpers."""

from django.utils import timezone

from .models import KYC_DOCUMENT_TYPES, User, UserDocument, UserKYC

KYC_IDENTITY_DOC_TYPES = ('id_card', 'passport', 'driver_license')


def get_or_create_kyc(user) -> UserKYC:
    kyc, _ = UserKYC.objects.get_or_create(user=user)
    return kyc


def mark_kyc_submitted(user) -> UserKYC:
    """Mark KYC as awaiting admin review after user updates details or uploads documents."""
    kyc = get_or_create_kyc(user)
    if kyc.status in ('approved',):
        return kyc
    kyc.status = 'under_review'
    if not kyc.submitted_at:
        kyc.submitted_at = timezone.now()
    kyc.save(update_fields=['status', 'submitted_at', 'updated_at'])
    return kyc


def get_kyc_documents(user):
    return UserDocument.objects.filter(
        user=user,
        document_type__in=KYC_DOCUMENT_TYPES,
    ).order_by('document_type', '-uploaded_at')


def approve_kyc(kyc: UserKYC, reviewer) -> UserKYC:
    kyc.status = 'approved'
    kyc.reviewed_by = reviewer
    kyc.reviewed_at = timezone.now()
    kyc.rejection_reason = ''
    kyc.save(
        update_fields=[
            'status',
            'reviewed_by',
            'reviewed_at',
            'rejection_reason',
            'updated_at',
        ]
    )

    user = kyc.user
    user.identity_verified = True
    user.save(update_fields=['identity_verified'])

    UserDocument.objects.filter(
        user=user,
        document_type__in=KYC_DOCUMENT_TYPES,
        status='pending',
    ).update(
        status='approved',
        verified_by=reviewer,
        verified_at=timezone.now(),
    )
    return kyc


def reject_kyc(kyc: UserKYC, reviewer, reason: str = '') -> UserKYC:
    kyc.status = 'rejected'
    kyc.reviewed_by = reviewer
    kyc.reviewed_at = timezone.now()
    kyc.rejection_reason = reason
    kyc.save(
        update_fields=[
            'status',
            'reviewed_by',
            'reviewed_at',
            'rejection_reason',
            'updated_at',
        ]
    )

    user = kyc.user
    user.identity_verified = False
    user.save(update_fields=['identity_verified'])
    return kyc
