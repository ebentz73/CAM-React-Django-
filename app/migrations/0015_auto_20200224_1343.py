# Generated by Django 3.0 on 2020-02-24 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_auto_20200224_1025'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='input',
            name='input_ds',
        ),
        migrations.RemoveField(
            model_name='input',
            name='input_page',
        ),
    ]
