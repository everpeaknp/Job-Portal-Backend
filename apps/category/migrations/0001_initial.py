from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tasks', '0009_category_listing_kind'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('tasks.category',),
        ),
    ]
