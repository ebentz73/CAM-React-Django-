# Generated by Django 3.0 on 2020-12-21 21:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_nodedata_input_data_set'),
    ]

    operations = [
        migrations.AddField(
            model_name='inputdataset',
            name='solution',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.AnalyticsSolution'),
        ),
    ]
