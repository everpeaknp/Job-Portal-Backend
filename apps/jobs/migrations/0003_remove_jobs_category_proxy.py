from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_job_category_proxy_models'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Category',
        ),
    ]
