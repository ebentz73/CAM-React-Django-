import tempfile
import uuid
from operator import attrgetter

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from polymorphic.models import PolymorphicModel

from app.utils import Sqlite


class Distribution(models.Model):
    low_value = models.DecimalField(max_digits=15, decimal_places=5)
    mid_value = models.DecimalField(max_digits=15, decimal_places=5)
    high_value = models.DecimalField(max_digits=15, decimal_places=5)

    class Meta:
        abstract = True


class BoundedDistribution(Distribution):
    lower_bound = models.DecimalField(max_digits=15, decimal_places=5)
    upper_bound = models.DecimalField(max_digits=15, decimal_places=5)

    class Meta:
        abstract = True


def _name_tam_file(*_):
    return f'tam_models/{uuid.uuid4().hex}'


class AnalyticsSolution(models.Model):
    name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now=True)
    tam_file = models.FileField(upload_to=_name_tam_file)

    def __str__(self):
        return f'Analytics Solution ({self.id}) - {self.name}'

    @property
    def models(self):
        return self.model_set.all()

    @property
    def scenarios(self):
        return self.scenario_set.all()


@receiver(post_save, sender=AnalyticsSolution)
def update_model(sender, **kwargs):
    solution = kwargs['instance']

    # Download file from GCS
    with tempfile.NamedTemporaryFile() as f:
        f.write(solution.tam_file.read())

        # Open sqlite file
        with Sqlite(f.name) as cursor:
            cursor.execute('SELECT * from TruNavModel')
            for model_record in cursor.fetchall():
                temp_model = Model(name=model_record[2], solution=solution)
                temp_model.save()
                cursor.execute('SELECT * from ModelDataPage where ModelId=? and pagetype=0', (model_record[1],))
                for data_page_record in cursor.fetchall():
                    temp_ip = InputPage(name=data_page_record[3], model=Model.objects.get(id=temp_model.id))
                    temp_ip.save()


class Model(models.Model):
    solution = models.ForeignKey(AnalyticsSolution, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    @property
    def input_pages(self):
        return self.inputpage_set.all()


class InputPage(models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    @property
    def input_data_sets(self):
        return self.inputdataset_set.all()

    @property
    def input_page_ds_ascs(self):
        return self.inputpagedsasc_set.all()


class Scenario(models.Model):
    solution = models.ForeignKey(AnalyticsSolution, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    @property
    def input_page_ds_ascs(self):
        return self.inputpagedsasc_set.all()


class InputDataSet(models.Model):
    input_page = models.ForeignKey(InputPage, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    @property
    def input_page_ds_ascs(self):
        return self.inputpagedsasc_set.all()

    @property
    def input_choice(self):
        return self.inputchoice_set.all()


class InputPageDsAsc(models.Model):
    input_page = models.ForeignKey(InputPage, on_delete=models.CASCADE, verbose_name='Input Page')
    ids = models.ForeignKey(InputDataSet, on_delete=models.CASCADE, verbose_name='Input Data Set')
    scenarios = models.ForeignKey(Scenario, on_delete=models.CASCADE, verbose_name='Scenario')


class ExecutiveView(models.Model):
    solution = models.ForeignKey(AnalyticsSolution, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    @property
    def inputs(self):
        return sorted(self.input_set.all(), key=attrgetter('order'))


class Input(models.Model):
    exec_view = models.ForeignKey(ExecutiveView, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    order = models.IntegerField(unique=True)

    def __str__(self):
        return self.name

    @property
    def input_choices(self):
        return self.inputchoice_set.all()


class InputChoice(PolymorphicModel):
    input = models.ForeignKey(Input, on_delete=models.CASCADE)
    ids = models.ForeignKey(InputDataSet, on_delete=models.CASCADE, verbose_name='Data Set')
    label = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.input}-{self.ids}'


class EvalJob(models.Model):
    solution = models.ForeignKey(AnalyticsSolution, on_delete=models.CASCADE)
    date_created = models.DateTimeField()
    status = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    source = models.IntegerField(editable=False)

    def __str__(self):
        return self.name


class NodeResult(models.Model):
    eval_job = models.ForeignKey(EvalJob, on_delete=models.CASCADE)
    scenario = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    node = models.CharField(max_length=255)
    layer = models.CharField(max_length=255)
    result_10 = models.FloatField()
    result_30 = models.FloatField()
    result_50 = models.FloatField()
    result_70 = models.FloatField()
    result_90 = models.FloatField()
