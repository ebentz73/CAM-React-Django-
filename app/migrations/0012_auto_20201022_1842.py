# Generated by Django 3.0 on 2020-10-22 23:42

import app.models
import app.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_merge_20201016_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenarionodedata',
            name='is_in_progress',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='inputdataset',
            name='file',
            field=models.FileField(upload_to='inputdatasets/', validators=[app.validators.validate_input_date_set_file]),
        ),
    ]
