# Generated by Django 3.0 on 2020-09-23 18:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_node_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilterCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('solution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.AnalyticsSolution')),
            ],
        ),
        migrations.CreateModel(
            name='FilterOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.FilterCategory')),
            ],
        ),
    ]