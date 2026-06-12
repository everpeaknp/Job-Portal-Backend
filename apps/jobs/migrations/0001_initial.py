from django.db import migrations





class Migration(migrations.Migration):



    initial = True



    dependencies = [

        ('tasks', '0008_task_cancellation_tracking'),

    ]



    operations = [

        migrations.CreateModel(

            name='Job',

            fields=[],

            options={

                'verbose_name': 'Job',

                'verbose_name_plural': 'Jobs',

                'proxy': True,

                'indexes': [],

                'constraints': [],

            },

            bases=('tasks.task',),

        ),

    ]

