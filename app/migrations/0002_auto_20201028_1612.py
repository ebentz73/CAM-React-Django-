# Generated by Django 3.0 on 2020-10-28 16:12

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DecimalNodeOverride',
            fields=[
                ('nodeoverride_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.NodeOverride')),
                ('value', models.DecimalField(decimal_places=5, max_digits=15)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('app.nodeoverride',),
        ),
        migrations.AddField(
            model_name='evaljob',
            name='errors',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='evaljob',
            name='layer_time_start',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='inputdataset',
            name='scenarios',
            field=models.ManyToManyField(blank=True, to='app.Scenario'),
        ),
        migrations.AlterField(
            model_name='noderesult',
            name='layer',
            field=models.DateField(),
        ),
        migrations.DeleteModel(
            name='IntegerNodeOverride',
        ),
    ]
