from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from django.db.models import Q
from polymorphic.models import PolymorphicModel

from app.mixins import ModelDiffMixin
from app.utils import ModelType
from app.validators import validate_input_date_set_file

__all__ = [
    'AnalyticsSolution',
    'ConstNodeData',
    'DecimalNodeOverride',
    'EvalJob',
    'FilterCategory',
    'FilterOption',
    'Input',
    'InputDataSet',
    'InputDataSetInput',
    'InputDataSetInputChoice',
    'InputNodeData',
    'InputPage',
    'Model',
    'Node',
    'NodeData',
    'NodeResult',
    'NumericInput',
    'Scenario',
    'SliderInput',
]


def NON_POLYMORPHIC_CASCADE(collector, field, sub_objs, using):
    return models.CASCADE(collector, field, sub_objs.non_polymorphic(), using)


class AnalyticsSolution(models.Model, ModelDiffMixin):
    TIME_OPTIONS = (
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('year', 'Year'),
    )
    ITERATIONS_OPTIONS = (
        (100, 100),
        (1000, 1000),
        (5000, 5000),
        (10000, 10000),
        (25000, 25000),
        (50000, 50000)
    )

    name = models.CharField(max_length=255)
    description = models.CharField(max_length=2048, null=True, blank=True)
    upload_date = models.DateTimeField(auto_now=True)
    tam_file = models.FileField(upload_to='tam_models/')
    dashboard_uid = models.CharField(max_length=40, editable=False, default='')
    dashboard_url = models.CharField(max_length=255, editable=False, default='')
    report_id = models.CharField(max_length=128, null=True, blank=True)
    workspace_id = models.CharField(max_length=128, null=True, blank=True)
    layer_time_increment = models.TextField(choices=TIME_OPTIONS)
    iterations = models.IntegerField(choices=ITERATIONS_OPTIONS, null=True)

    def __str__(self):
        return f'Analytics Solution ({self.id}) - {self.name}'

    @property
    def models(self) -> ModelType['Model']:
        return self.model_set.all()

    @property
    def scenarios(self) -> ModelType['Scenario']:
        return self.scenario_set.filter(is_adhoc=False)

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


class Scenario(models.Model):
    solution = models.ForeignKey(AnalyticsSolution, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_adhoc = models.BooleanField(default=False)
    is_in_progress = models.BooleanField(default=False)
    status = models.CharField(max_length=256, null=True, blank=True)
    layer_date_start = models.DateField()
    shared = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name

    @property
    def node_overrides(self) -> ModelType['NodeOverride']:
        return self.nodeoverride_set.all()

    @property
    def node_data(self) -> ModelType['NodeData']:
        return self.nodedata_set.all()

    @property
    def node_results(self) -> ModelType['NodeResult']:
        return self.noderesult_set.all()


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
    tags = ArrayField(models.CharField(max_length=255), default=list)
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

    @property
    def node_data(self) -> ModelType['NodeData']:
        return self.nodedata_set.all()


class InputDataSet(models.Model):
    input_page = models.ForeignKey(InputPage, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='inputdatasets/', validators=[validate_input_date_set_file])
    scenarios = models.ManyToManyField(Scenario, blank=True, related_name='input_data_sets')

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
    layer_time_start = models.DateField(null=True)
    layer_time_increment = models.TextField(null=True, choices=TIME_OPTIONS)
    errors = JSONField(null=True)

    def __str__(self):
        return self.name

    def is_complete(self):
        return self.status == 'Complete.'


class NodeResult(models.Model):
    scenario_id = models.ForeignKey(Scenario, on_delete=models.CASCADE, db_column='scenario_id')
    scenario = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    node = models.CharField(max_length=255)
    layer = models.DateField()
    node_tags = JSONField()
    role = models.CharField(max_length=255, null=True, editable=False)
    result_10 = models.FloatField()
    result_30 = models.FloatField()
    result_50 = models.FloatField()
    result_70 = models.FloatField()
    result_90 = models.FloatField()

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.role = next(
            (tag.split('==')[1] for tag in self.node_tags if tag.startswith('CAM_ROLE==')),
            None,
        )
        super().save(force_insert, force_update, using, update_fields)


class Input(PolymorphicModel):
    solution = models.ForeignKey(AnalyticsSolution, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class InputDataSetInput(Input):
    @property
    def input_choices(self) -> ModelType['InputDataSetInputChoice']:
        return self.inputdatasetinputchoice_set.all()


class InputDataSetInputChoice(models.Model):
    input = models.ForeignKey(InputDataSetInput, on_delete=models.CASCADE, related_name='choices')
    ids = models.ForeignKey(InputDataSet, on_delete=models.CASCADE, verbose_name='Data Set')
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label


class NumericInput(Input):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)


class SliderInput(Input):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    minimum = models.FloatField()
    maximum = models.FloatField()
    step = models.FloatField()


class NodeOverride(PolymorphicModel):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)


class DecimalNodeOverride(NodeOverride):
    value = models.DecimalField(max_digits=15, decimal_places=5)


class NodeData(PolymorphicModel):
    node = models.ForeignKey(Node, on_delete=NON_POLYMORPHIC_CASCADE, default=None)
    is_model = models.BooleanField(default=True)
    scenario = models.ForeignKey(Scenario, on_delete=NON_POLYMORPHIC_CASCADE, default=None, null=True)


class InputNodeData(NodeData):
    default_data = ArrayField(ArrayField(models.DecimalField(max_digits=15, decimal_places=5)))


class ConstNodeData(NodeData):
    default_data = ArrayField(models.DecimalField(max_digits=15, decimal_places=5))


class FilterCategory(models.Model):
    solution = models.ForeignKey(AnalyticsSolution, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


class FilterOption(models.Model):
    category = models.ForeignKey(FilterCategory, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255)
    tag = models.CharField(max_length=255, default='')
