from operator import attrgetter

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel
from django.contrib.postgres.fields import JSONField
import psycopg2
from cloud_analysis_manager.settings import DATABASES as db
import logging


class Tables(models.Model):
    db_detail = db["default"]
    conn = psycopg2.connect(dbname= db_detail["NAME"],user=db_detail["USER"],
                            host=db_detail["HOST"],password=db_detail["PASSWORD"])
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public' AND table_type='BASE TABLE'")
    table = cur.fetchall()


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


class AnalyticsSolution(models.Model):
    name = models.CharField(max_length=255)
    upload_date = models.DateTimeField()
    file_url = models.URLField(max_length=255)

    def __str__(self):
        return f'EvalJob ({self.id}) - {self.name}'

    @property
    def models(self):
        return self.model_set.all()

    @property
    def scenarios(self):
        return self.scenario_set.all()


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
    '''
    @property
    def nodes(self):
        return self.node_set.all()
'''


class Scenario(models.Model):
    solution = models.ForeignKey(AnalyticsSolution, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    @property
    def scenario_data_sets(self):
        return self.scenariodataset_set.all()

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

    @property
    def input_data_sets(self):
        return self.inputdataset_set.all()


class InputPageDsAsc(BoundedDistribution):
    inputPage = models.ForeignKey(InputPage, on_delete=models.CASCADE, verbose_name='Input Page')
    ids = models.ForeignKey(InputDataSet, on_delete=models.CASCADE, verbose_name='Input Data Set')
    scenarios = models.ForeignKey(Scenario, on_delete=models.CASCADE, verbose_name='Scenario')


class ScenarioDataSet(models.Model):
    # TODO: is https://django-select2.readthedocs.io/en/latest/index.html useful?
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    ids = models.ForeignKey(InputDataSet, on_delete=models.CASCADE)


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
    name = models.CharField(max_length=255)
    input = models.ForeignKey(Input, on_delete=models.CASCADE)
    ids = models.ForeignKey(InputDataSet, on_delete=models.CASCADE)
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label

'''
class InputChoice(PolymorphicModel):
    name = models.CharField(max_length=255)
    input = models.ForeignKey(Input, on_delete=models.CASCADE)
    ids = models.ForeignKey(InputDataSet, on_delete=models.CASCADE)
    #ids = models.ForeignKey(InputDataSet, on_delete=models.CASCADE, verbose_name='Input Data Set')
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label

    def clean(self):
        # allow only one type of input choice for each input
        if any(not isinstance(x, type(self)) for x in self.input.input_choices):
            raise ValidationError(_('An input can only have one type of input choice.'))
'''


class EvalJob(models.Model):
    solution = models.ForeignKey(AnalyticsSolution, on_delete=models.CASCADE)
    definition = JSONField()
    DateCreated = models.DateTimeField()
    Status = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

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



'''
class EvalJob(models.Model):
    name = models.CharField(max_length=255)
    upload_date = models.DateTimeField()
    file_url = models.CharField(max_length=255)

    def __str__(self):
        return f'EvalJob ({self.id}) - {self.name}'

    @property
    def models(self):
        return self.model_set.all()

    @property
    def scenarios(self):
        return self.scenario_set.all()


class Model(models.Model):
    eval_job = models.ForeignKey(EvalJob, on_delete=models.CASCADE)
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
    def nodes(self):
        return self.node_set.all()

    @property
    def input_data_sets(self):
        return self.inputdataset_set.all()


class Node(models.Model):
    input_page = models.ForeignKey(InputPage, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    @property
    def ids_node(self):
        return self.inputdatasetnode


class InputDataSet(models.Model):
    input_page = models.ForeignKey(InputPage, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    @property
    def ids_nodes(self):
        return self.inputdatasetnode_set.all()

    @property
    def input_choice(self):
        return self.inputchoice


class InputDataSetNode(BoundedDistribution):
    node = models.OneToOneField(Node, on_delete=models.CASCADE)
    ids = models.ForeignKey(InputDataSet, on_delete=models.CASCADE, verbose_name='Input Data Set')


class Scenario(models.Model):
    eval_job = models.ForeignKey(EvalJob, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ScenarioDataSet(models.Model):
    # TODO: is https://django-select2.readthedocs.io/en/latest/index.html useful?
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    ids = models.ForeignKey(InputDataSet, on_delete=models.CASCADE)


class ExecutiveView(models.Model):
    eval_job = models.ForeignKey(EvalJob, on_delete=models.CASCADE)

    @property
    def inputs(self):
        return sorted(self.input_set.all(), key=attrgetter('order'))


class Input(models.Model):
    exec_view = models.ForeignKey(ExecutiveView, on_delete=models.CASCADE)
    label = models.CharField(max_length=255)
    order = models.IntegerField(unique=True)

    def __str__(self):
        return self.label

    @property
    def input_choices(self):
        return self.inputchoice_set.all()

    # def clean(self):
    #     # allow only one type of input choice for each input
    #     if any(not isinstance(x, type(self.input_choices.first())) for x in self.input_choices):
    #         raise ValidationError(_)


class InputChoice(PolymorphicModel):
    input = models.ForeignKey(Input, on_delete=models.CASCADE)
    ids = models.OneToOneField(InputDataSet, on_delete=models.CASCADE)
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label

    def clean(self):
        # allow only one type of input choice for each input
        if any(not isinstance(x, type(self)) for x in self.input.input_choices):
            raise ValidationError(_('An input can only have one type of input choice.'))


class ConstantChoice(InputChoice):
    value = models.CharField(max_length=255)


class DistributionDropdownChoice(InputChoice, Distribution):
    pass


class DistributionSliderChoice(InputChoice, Distribution):
    step = models.DecimalField(max_digits=15, decimal_places=5)

class AnalyticsJob(models.Model):
    eval_job = models.ForeignKey(EvalJob, on_delete=models.CASCADE)
    definition = JSONField()
    Result = JSONField()
    #DateCreated=models.DateTimeField()
    #Status=models.CharField(max_length=255)
'''