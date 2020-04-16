import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q
from polymorphic.models import PolymorphicModel

__all__ = [
    'AnalyticsSolution',
    'EvalJob',
    'ExecutiveView',
    'IntegerNodeOverride',
    'Input',
    'InputChoice',
    'InputDataSet',
    'InputDataSetInput',
    'InputDataSetInputChoice',
    'InputPage',
    'Model',
    'Node',
    'NodeResult',
    'NumericInput',
    'Scenario',
    'SliderInput',
]

from app.utils import ModelType


def _name_tam_file(*_):
    return f'tam_models/{uuid.uuid4().hex}'


class AnalyticsSolution(models.Model):
    name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now=True)
    tam_file = models.FileField(upload_to=_name_tam_file)

    def __str__(self):
        return f'Analytics Solution ({self.id}) - {self.name}'

    @property
    def models(self) -> ModelType['Model']:
        return self.model_set.all()

    @property
    def scenarios(self) -> ModelType['Scenario']:
        return self.scenario_set.filter(is_adhoc=False)


class Scenario(models.Model):
    solution = models.ForeignKey(AnalyticsSolution, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_adhoc = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def input_data_sets(self) -> ModelType['InputDataSet']:
        return self.inputdataset_set.all()

    @property
    def node_overrides(self) -> ModelType['NodeOverride']:
        return self.nodeoverride_set.all()


class Model(models.Model):
    solution = models.ForeignKey(AnalyticsSolution, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    tam_id = models.UUIDField(editable=False)

    def __str__(self):
        return self.name

    @property
    def input_pages(self) -> ModelType['InputPage']:
        return self.inputpage_set.all()

    @property
    def nodes(self) -> ModelType['Node']:
        return self.node_set.all()


class InputPage(models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    tam_id = models.UUIDField(editable=False)

    def __str__(self):
        return self.name

    @property
    def input_data_sets(self) -> ModelType['InputDataSet']:
        return self.inputdataset_set.all()


class Node(models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    tam_id = models.UUIDField(editable=False)

    def __str__(self):
        return self.name

    @property
    def node_overrides(self) -> ModelType['NodeOverride']:
        return self.nodeoverride_set.all()

    @property
    def numeric_inputs(self) -> ModelType['NumericInput']:
        return self.numericinput_set.all()

    @property
    def slider_inputs(self) -> ModelType['SliderInput']:
        return self.sliderinput_set.all()


def _name_ids_file(*_):
    return f'inputdatasets/{uuid.uuid4().hex}'


class InputDataSet(models.Model):
    input_page = models.ForeignKey(InputPage, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=_name_ids_file)
    scenarios = models.ManyToManyField(Scenario, blank=True)

    def __str__(self):
        return self.name

    @property
    def input_choices(self) -> ModelType['InputDataSetInputChoice']:
        return self.inputdatasetinputchoice_set.all()


class EvalJob(models.Model):
    TIME_OPTIONS = (
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('year', 'Year'),
    )

    name = models.CharField(max_length=255)
    solution = models.ForeignKey(AnalyticsSolution, on_delete=models.CASCADE)
    adhoc_scenario = models.OneToOneField(Scenario, on_delete=models.CASCADE)
    date_created = models.DateTimeField()
    status = models.CharField(max_length=255)
    layer_time_start = models.DateTimeField(null=True)
    layer_time_increment = models.TextField(null=True, choices=TIME_OPTIONS)

    def __str__(self):
        return self.name

    @property
    def node_results(self) -> ModelType['NodeResult']:
        return self.noderesult_set.all()


class NodeResult(models.Model):
    eval_job = models.ForeignKey(EvalJob, on_delete=models.CASCADE)
    scenario = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    node = models.CharField(max_length=255)
    layer = models.DateField()
    node_tags = JSONField()
    result_10 = models.FloatField()
    result_30 = models.FloatField()
    result_50 = models.FloatField()
    result_70 = models.FloatField()
    result_90 = models.FloatField()


class ExecutiveView(models.Model):
    name = models.CharField(max_length=255)
    solution = models.ForeignKey(AnalyticsSolution, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def inputs(self) -> ModelType['Input']:
        return self.input_set.all()

    @property
    def ids_inputs(self) -> ModelType['InputDataSetInput']:
        return self.input_set.filter(Q(instance_of=InputDataSetInput))

    @property
    def numeric_inputs(self) -> ModelType['NumericInput']:
        return self.input_set.filter(Q(instance_of=NumericInput))

    @property
    def slider_inputs(self) -> ModelType['SliderInput']:
        return self.input_set.filter(Q(instance_of=SliderInput))


class Input(PolymorphicModel):
    exec_view = models.ForeignKey(ExecutiveView, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class InputChoice(models.Model):
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label


class InputDataSetInput(Input):

    @property
    def input_choices(self) -> ModelType['InputChoice']:
        return self.inputdatasetinputchoice_set.all()


class InputDataSetInputChoice(InputChoice):
    input = models.ForeignKey(InputDataSetInput, on_delete=models.CASCADE)
    ids = models.ForeignKey(InputDataSet, on_delete=models.CASCADE, verbose_name='Data Set')


class NumericInput(Input):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)


class SliderInput(Input):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    minimum = models.DecimalField(max_digits=15, decimal_places=5)
    maximum = models.DecimalField(max_digits=15, decimal_places=5)
    step = models.DecimalField(max_digits=15, decimal_places=5)


class NodeOverride(PolymorphicModel):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)


class IntegerNodeOverride(NodeOverride):
    value = models.IntegerField()
