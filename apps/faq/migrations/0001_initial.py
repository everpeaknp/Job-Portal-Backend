import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='FaqItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question', models.CharField(max_length=500)),
                ('answer', models.TextField()),
                (
                    'category',
                    models.CharField(
                        choices=[('general', 'General'), ('services', 'Services')],
                        db_index=True,
                        default='general',
                        max_length=50,
                    ),
                ),
                ('is_published', models.BooleanField(db_index=True, default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'FAQ item',
                'verbose_name_plural': 'FAQ items',
                'ordering': ['sort_order', 'question'],
                'indexes': [
                    models.Index(fields=['category', 'is_published', 'sort_order'], name='faq_faqitem_cat_pub_sort_idx'),
                ],
            },
        ),
    ]
