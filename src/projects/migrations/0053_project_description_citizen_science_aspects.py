# Generated by Django 2.2.13 on 2021-04-30 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0052_auto_20201104_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='description_citizen_science_aspects',
            field=models.CharField(default='Field added at the beginning of May for moderation purposes', max_length=2000),
            preserve_default=False,
        ),
    ]
