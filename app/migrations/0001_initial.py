# Generated by Django 2.2 on 2020-04-07 22:03

import app.models
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalyticsSolution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('upload_date', models.DateTimeField(auto_now=True)),
                ('tam_file', models.FileField(upload_to=app.models._name_tam_file)),
            ],
        ),
        migrations.CreateModel(
            name='EvalJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField()),
                ('status', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('layer_time_start', models.DateTimeField(null=True)),
                ('layer_time_increment', models.TextField(choices=[('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year')], null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExecutiveView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('solution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.AnalyticsSolution')),
            ],
        ),
        migrations.CreateModel(
            name='Input',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('exec_view', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.ExecutiveView')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_app.input_set+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='InputChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('tam_id', models.UUIDField(editable=False)),
                ('solution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.AnalyticsSolution')),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('tam_id', models.UUIDField(editable=False)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Model')),
            ],
        ),
        migrations.CreateModel(
            name='NodeOverride',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Node')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_app.nodeoverride_set+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='InputDataSetInput',
            fields=[
                ('input_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.Input')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('app.input',),
        ),
        migrations.CreateModel(
            name='IntegerNodeOverride',
            fields=[
                ('nodeoverride_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.NodeOverride')),
                ('value', models.IntegerField()),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('app.nodeoverride',),
        ),
        migrations.CreateModel(
            name='Scenario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('is_adhoc', models.BooleanField(default=False)),
                ('solution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.AnalyticsSolution')),
            ],
        ),
        migrations.CreateModel(
            name='NodeResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scenario', models.CharField(max_length=255)),
                ('model', models.CharField(max_length=255)),
                ('node', models.CharField(max_length=255)),
                ('layer', models.CharField(max_length=255)),
                ('node_tags', django.contrib.postgres.fields.jsonb.JSONField()),
                ('result_10', models.FloatField()),
                ('result_30', models.FloatField()),
                ('result_50', models.FloatField()),
                ('result_70', models.FloatField()),
                ('result_90', models.FloatField()),
                ('eval_job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.EvalJob')),
            ],
        ),
        migrations.AddField(
            model_name='nodeoverride',
            name='scenario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Scenario'),
        ),
        migrations.CreateModel(
            name='InputPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('tam_id', models.UUIDField(editable=False)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Model')),
            ],
        ),
        migrations.CreateModel(
            name='InputDataSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to=app.models._name_ids_file)),
                ('input_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.InputPage')),
                ('scenarios', models.ManyToManyField(to='app.Scenario')),
            ],
        ),
        migrations.AddField(
            model_name='evaljob',
            name='adhoc_scenario',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.Scenario'),
        ),
        migrations.AddField(
            model_name='evaljob',
            name='solution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.AnalyticsSolution'),
        ),
        migrations.CreateModel(
            name='SliderInput',
            fields=[
                ('input_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.Input')),
                ('minimum', models.DecimalField(decimal_places=5, max_digits=15)),
                ('maximum', models.DecimalField(decimal_places=5, max_digits=15)),
                ('step', models.DecimalField(decimal_places=5, max_digits=15)),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Node')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('app.input',),
        ),
        migrations.CreateModel(
            name='NumericInput',
            fields=[
                ('input_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.Input')),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Node')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('app.input',),
        ),
        migrations.CreateModel(
            name='InputDataSetInputChoice',
            fields=[
                ('inputchoice_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.InputChoice')),
                ('ids', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.InputDataSet', verbose_name='Data Set')),
                ('input', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.InputDataSetInput')),
            ],
            bases=('app.inputchoice',),
        ),
    ]
