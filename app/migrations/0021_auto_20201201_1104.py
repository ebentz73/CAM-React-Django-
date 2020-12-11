# Generated by Django 3.0 on 2020-12-01 17:04

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_auto_20201120_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='analyticssolution',
            name='layer_time_increment',
            field=models.TextField(choices=[('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year')], default='month'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='scenario',
            name='layer_date_start',
            field=models.DateField(default=datetime.datetime(2020, 12, 1, 17, 4, 40, 377813, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
