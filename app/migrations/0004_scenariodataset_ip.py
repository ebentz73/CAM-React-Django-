# Generated by Django 3.0 on 2020-03-06 19:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_noderesult'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenariodataset',
            name='ip',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.InputPage'),
        ),
    ]
