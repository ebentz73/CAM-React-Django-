import uuid
from operator import attrgetter

from django.db import models

__all__ = [
    'AnalyticsSolution',
    'EvalJob',
    'ExecutiveView',
    'Input',
    'InputChoice',
    'InputDataSet',
    'InputPage',
    'Model',
    'NodeResult',
    'Scenario',
]


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
        return self.scenario_set.filter(is_adhoc=False)


class Scenario(models.Model):
    solution = models.ForeignKey(AnalyticsSolution, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_adhoc = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def input_data_sets(self):
        return self.inputdataset_set.all()


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


def _name_ids_file(*_):
    return f'inputdatasets/{uuid.uuid4().hex}'


class InputDataSet(models.Model):
    input_page = models.ForeignKey(InputPage, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=_name_ids_file)
    scenarios = models.ManyToManyField(Scenario)

    def __str__(self):
        return self.name

    @property
    def input_choices(self):
        return self.inputchoice_set.all()


class EvalJob(models.Model):
    solution = models.ForeignKey(AnalyticsSolution, on_delete=models.CASCADE)
    adhoc_scenario = models.OneToOneField(Scenario, on_delete=models.CASCADE)
    date_created = models.DateTimeField()
    status = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    @property
    def node_results(self):
        return self.noderesult_set.all()


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

    def __str__(self):
        return self.name

    @property
    def input_choices(self):
        return self.inputchoice_set.all()


class InputChoice(models.Model):
    input = models.ForeignKey(Input, on_delete=models.CASCADE)
    ids = models.ForeignKey(InputDataSet, on_delete=models.CASCADE, verbose_name='Data Set')
    label = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.input}-{self.ids}'
