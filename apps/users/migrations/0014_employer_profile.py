# Generated manually for employer business profiles

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_userskill_details'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployerProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('account_type', models.CharField(choices=[('individual', 'Individual'), ('company', 'Company')], default='individual', max_length=20)),
                ('company_name', models.CharField(blank=True, max_length=255)),
                ('industry', models.CharField(blank=True, max_length=120)),
                ('team_size', models.CharField(blank=True, max_length=80)),
                ('website', models.URLField(blank=True)),
                ('cost_range', models.CharField(blank=True, max_length=120)),
                ('contact_email', models.EmailField(blank=True, max_length=254)),
                ('contact_phone', models.CharField(blank=True, max_length=30)),
                ('logo_color', models.CharField(default='serif-m', max_length=40)),
                ('logo_text', models.CharField(default='CO', max_length=8)),
                ('logo_image', models.ImageField(blank=True, null=True, upload_to='employer_logos/')),
                ('is_public', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='employer_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'employer_profiles',
            },
        ),
        migrations.CreateModel(
            name='EmployerGalleryImage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('image', models.ImageField(upload_to='employer_gallery/')),
                ('alt_text', models.CharField(blank=True, max_length=255)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery_images', to='users.employerprofile')),
            ],
            options={
                'db_table': 'employer_gallery_images',
                'ordering': ['sort_order', 'created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='employerprofile',
            index=models.Index(fields=['account_type'], name='employer_pr_account_6f0f0d_idx'),
        ),
        migrations.AddIndex(
            model_name='employerprofile',
            index=models.Index(fields=['is_public'], name='employer_pr_is_publ_0d8f2a_idx'),
        ),
        migrations.AddIndex(
            model_name='employergalleryimage',
            index=models.Index(fields=['profile', 'sort_order'], name='employer_ga_profile_2f0a8b_idx'),
        ),
    ]
