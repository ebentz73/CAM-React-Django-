# Generated by Django 3.0 on 2020-02-11 18:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20200211_1128'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inputchoice',
            options={},
        ),
        migrations.RemoveField(
            model_name='inputchoice',
            name='polymorphic_ctype',
        ),
        migrations.AlterField(
            model_name='inputchoice',
            name='ids',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.InputDataSet', verbose_name='Input Data Set'),
        ),
    ]