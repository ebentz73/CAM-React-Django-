# Generated by Django 3.0 on 2020-12-10 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_auto_20201204_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='analyticssolution',
            name='layer_offset',
            field=models.IntegerField(default=0),
        ),
    ]
