from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
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
        migrations.CreateModel(
            name='JobQuestion',
            fields=[],
            options={
                'verbose_name': 'Job question',
                'verbose_name_plural': 'Job questions',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('tasks.taskquestion',),
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[],
            options={
                'verbose_name': 'Bid',
                'verbose_name_plural': 'Bids',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('bids.bid',),
        ),
    ]
