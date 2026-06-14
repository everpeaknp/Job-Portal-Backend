import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_employer_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserKYC',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    'pan_number',
                    models.CharField(
                        blank=True,
                        help_text='Permanent Account Number (PAN) submitted with identity verification.',
                        max_length=20,
                    ),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('not_started', 'Not started'),
                            ('pending', 'Pending review'),
                            ('under_review', 'Under review'),
                            ('approved', 'Approved'),
                            ('rejected', 'Rejected'),
                        ],
                        db_index=True,
                        default='not_started',
                        max_length=20,
                    ),
                ),
                (
                    'admin_notes',
                    models.TextField(
                        blank=True,
                        help_text='Internal notes for admins (not shown to the user).',
                    ),
                ),
                (
                    'rejection_reason',
                    models.TextField(
                        blank=True,
                        help_text='Reason shown to the user when verification is rejected.',
                    ),
                ),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'reviewed_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='kyc_reviews',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'user',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='kyc',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'KYC',
                'verbose_name_plural': 'KYC',
                'db_table': 'user_kyc',
            },
        ),
    ]
