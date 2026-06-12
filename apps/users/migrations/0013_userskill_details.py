from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_user_google_id_facebook_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='userskill',
            name='details',
            field=models.TextField(blank=True, default=''),
        ),
    ]
