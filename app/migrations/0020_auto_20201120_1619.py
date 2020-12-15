# Generated by Django 3.0 on 2020-11-20 22:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_merge_20201028_1311'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='input',
            name='exec_view',
        ),
        migrations.RemoveField(
            model_name='inputdatasetinputchoice',
            name='inputchoice_ptr',
        ),
        migrations.AddField(
            model_name='input',
            name='solution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.AnalyticsSolution'),
        ),
        migrations.AlterField(
            model_name='inputdataset',
            name='scenarios',
            field=models.ManyToManyField(blank=True, related_name='input_data_sets', to='app.Scenario'),
        ),
        migrations.AlterField(
            model_name='inputdatasetinputchoice',
            name='input',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices',
                                    to='app.InputDataSetInput'),
        ),
        migrations.AlterField(
            model_name='sliderinput',
            name='maximum',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='sliderinput',
            name='minimum',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='sliderinput',
            name='step',
            field=models.FloatField(),
        ),
        migrations.DeleteModel(
            name='ExecutiveView',
        ),
        migrations.DeleteModel(
            name='InputChoice',
        ),
        migrations.DeleteModel(
            name='InputDataSetInputChoice',
        ),
        migrations.CreateModel(
            name='InputDataSetInputChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255)),
                ('ids', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.InputDataSet',
                                          verbose_name='Data Set')),
                ('input', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.InputDataSetInput')),
            ],
        ),
    ]
