import uuid

from django.db import migrations, models
from django.utils.text import slugify


CANONICAL_LANGUAGES = [
    'English',
    'Nepali',
    'Spanish',
    'German',
    'French',
    'Hindi',
]


def dedupe_by_name(apps, schema_editor):
    Language = apps.get_model('language', 'Language')
    seen: set[str] = set()
    for lang in Language.objects.order_by('order', 'name', 'listing_kind'):
        key = lang.name.lower()
        if key in seen:
            lang.delete()
        else:
            seen.add(key)


def reseed_languages(apps, schema_editor):
    Locale = apps.get_model('language', 'Locale')
    Locale.objects.all().delete()
    for order, name in enumerate(CANONICAL_LANGUAGES):
        slug = slugify(name)[:100]
        Locale.objects.create(
            id=uuid.uuid4(),
            name=name,
            slug=slug,
            order=order,
            is_active=True,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('language', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='language',
            name='marketplace_languages_name_listing_kind_uniq',
        ),
        migrations.RemoveConstraint(
            model_name='language',
            name='marketplace_languages_slug_listing_kind_uniq',
        ),
        migrations.RunPython(dedupe_by_name, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='language',
            name='listing_kind',
        ),
        migrations.AlterModelOptions(
            name='language',
            options={
                'ordering': ['order', 'name'],
                'verbose_name': 'Language',
                'verbose_name_plural': 'Languages',
            },
        ),
        migrations.RenameModel(
            old_name='Language',
            new_name='Locale',
        ),
        migrations.RunPython(reseed_languages, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='locale',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='locale',
            name='slug',
            field=models.SlugField(max_length=100, unique=True),
        ),
    ]
