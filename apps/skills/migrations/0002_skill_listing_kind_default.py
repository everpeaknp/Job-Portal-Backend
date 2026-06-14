from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skill',
            name='listing_kind',
            field=models.CharField(
                choices=[
                    ('task', 'Task'),
                    ('service', 'Service'),
                    ('project', 'Project'),
                    ('job', 'Job'),
                ],
                db_index=True,
                default='project',
                help_text='Which listing type this skill applies to (job, project, or service).',
                max_length=20,
            ),
        ),
    ]
