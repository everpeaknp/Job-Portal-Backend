from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tasks', '0008_task_cancellation_tracking'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[],
            options={
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('tasks.task',),
        ),
    ]
