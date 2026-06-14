from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tasks', '0012_taskview_referrer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[],
            options={
                'verbose_name': 'Bookmark',
                'verbose_name_plural': 'Bookmarks',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('tasks.taskbookmark',),
        ),
    ]
