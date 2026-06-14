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


def reorder_languages(apps, schema_editor):
    Locale = apps.get_model('language', 'Locale')
    for order, name in enumerate(NEPAL_LANGUAGES):
        slug = slugify(name)[:100]
        updated = Locale.objects.filter(name=name).update(order=order, slug=slug, is_active=True)
        if not updated:
            Locale.objects.create(
                id=uuid.uuid4(),
                name=name,
                slug=slug,
                order=order,
                is_active=True,
            )


class Migration(migrations.Migration):

    dependencies = [
        ('language', '0003_seed_nepal_languages'),
    ]

    operations = [
        migrations.RunPython(reorder_languages, migrations.RunPython.noop),
    ]
