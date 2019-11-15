import mongoengine
from mongoengine import Document, fields


class EvalJob(Document):
    # _id = fields.StringField(required=True, primary_key=True)
    name = fields.StringField(required=True)
    model_url = fields.StringField(required=True)
    layers = fields.ListField(required=True)
    nodes = fields.ListField(required=True)


class BaselineConfig(Document):
    # _id = fields.StringField(required=True, primary_key=True)
    name = fields.StringField(required=True)
    eval_job_id = fields.ReferenceField(EvalJob, reverse_delete_rule=mongoengine.CASCADE, required=True)
    baseline_values = fields.DynamicField(required=True)
    result_url = fields.StringField(required=True)
    eval_time = fields.DateTimeField(required=True)


class Scenario(Document):
    # _id = fields.StringField(required=True, primary_key=True)
    name = fields.StringField(required=True)
    baseline_config_id = fields.ReferenceField(BaselineConfig, reverse_delete_rule=mongoengine.CASCADE, required=True)
    override_values = fields.DynamicField(required=True)
