# Generated by Django 3.0 on 2020-12-15 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_node_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='analyticssolution',
            name='support_contact',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='analyticssolution',
            name='user_guide_file',
            field=models.FileField(blank=True, upload_to='user_guides/'),
        ),
    ]