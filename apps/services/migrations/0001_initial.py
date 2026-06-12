from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tasks', '0008_task_cancellation_tracking'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[],
            options={
                'verbose_name': 'Service',
                'verbose_name_plural': 'Services',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('tasks.task',),
        ),
    ]
