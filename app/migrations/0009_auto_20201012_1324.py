# Generated by Django 3.0 on 2020-10-12 18:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20200928_1559'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scenarionodedata',
            name='name',
        ),
        migrations.RemoveField(
            model_name='scenarionodedata',
            name='overrides',
        ),
        migrations.AddField(
            model_name='scenarionodedata',
            name='node_data',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='app.NodeData'),
        ),
        migrations.AddField(
            model_name='analyticssolution',
            name='report_id',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='analyticssolution',
            name='workspace_id',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]