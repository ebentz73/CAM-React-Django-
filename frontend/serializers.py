from rest_framework import serializers
from .models import EvalJob, NodeData, ScenarioNodeData


class EvalJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvalJob
        fields = (
            "id",
            "title",
            "date_created",
            "status",
            "layer_time_start",
            "layer_time_increment",
            "errors",
        )


class NodeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeData
        fields = ("id", "title", "defaults")


class ScenarioNodeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioNodeData
        fields = (
            "id",
            "title",
            "overrides",
            "is_uncertain",
            "is_bounded",
            "is_changes",
        )
