import uuid

from django.db import migrations
from django.utils.text import slugify


NEPAL_LANGUAGES = [
    'English',
    'Nepali',
    'Hindi',
    'Maithili',
    'Bhojpuri',
    'Tharu',
    'Tamang',
    'Newari',
    'Magar',
    'Gurung',
    'Sherpa',
    'Limbu',
    'Rai',
    'Awadhi',
    'Doteli',
    'Urdu',
    'Bajjika',
    'French',
    'German',
    'Spanish',
]


def add_nepal_languages(apps, schema_editor):
    Locale = apps.get_model('language', 'Locale')
    for order, name in enumerate(NEPAL_LANGUAGES):
        slug = slugify(name)[:100]
        Locale.objects.get_or_create(
            name=name,
            defaults={
                'id': uuid.uuid4(),
                'slug': slug,
                'order': order,
                'is_active': True,
            },
        )


def remove_nepal_languages(apps, schema_editor):
    Locale = apps.get_model('language', 'Locale')
    added = {
        'Maithili',
        'Bhojpuri',
        'Tharu',
        'Tamang',
        'Newari',
        'Magar',
        'Gurung',
        'Sherpa',
        'Limbu',
        'Rai',
        'Awadhi',
        'Doteli',
        'Urdu',
        'Bajjika',
    }
    Locale.objects.filter(name__in=added).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('language', '0002_dedupe_languages_rename_locale'),
    ]

    operations = [
        migrations.RunPython(add_nepal_languages, remove_nepal_languages),
    ]
