# Generated by Django 3.0 on 2020-10-26 22:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20201022_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='nodedata',
            name='scenario',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='app.Scenario'),
        ),
    ]
