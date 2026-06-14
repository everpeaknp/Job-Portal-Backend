from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0011_seed_nepal_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskview',
            name='referrer',
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
    ]
