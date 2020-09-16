import uuid

from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from django.db.models import Q
from polymorphic.models import PolymorphicModel

from app.utils import ModelType, create_dashboard
from app.mixins import ModelDiffMixin

__all__ = ["EvalJob", "NodeData", "ScenarioNodeData"]


class EvalJob(models.Model):
    TIME_OPTIONS = (
        ("day", "Day"),
        ("week", "Week"),
        ("month", "Month"),
        ("year", "Year"),
    )

    title = models.CharField(max_length=255)
    date_created = models.DateTimeField()
    status = models.CharField(max_length=255)
    layer_time_start = models.DateField(null=True)
    layer_time_increment = models.TextField(null=True, choices=TIME_OPTIONS)
    errors = JSONField(null=True)


class NodeData(models.Model):
    title = models.CharField(max_length=255)
    defaults = ArrayField(models.IntegerField())


class ScenarioNodeData(models.Model):
    title = models.CharField(max_length=255)
    overrides = ArrayField(models.IntegerField())
    is_uncertain = models.BooleanField(default=False)
    is_bounded = models.BooleanField(default=False)
    is_changes = models.BooleanField(default=False)
