# Generated by Django 3.0 on 2020-02-24 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_remove_input_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='input',
            name='input_ds',
            field=models.CharField(default='NA', max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='input',
            name='input_page',
            field=models.CharField(default='NA', max_length=250),
            preserve_default=False,
        ),
    ]