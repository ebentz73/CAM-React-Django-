from operator import attrgetter

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel


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
