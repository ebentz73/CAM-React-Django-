import uuid

from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from django.db.models import Q
from polymorphic.models import PolymorphicModel

from app.utils import ModelType, create_dashboard
from app.mixins import ModelDiffMixin
