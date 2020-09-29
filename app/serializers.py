from rest_framework import serializers

from app.models import AnalyticsSolution, EvalJob, NodeResult, \
    Scenario, NodeData, ScenarioNodeData, Node, Model, InputNodeData, ConstNodeData, FilterOption, FilterCategory
from app.utils import GoogleCloudStorage


class EvalJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvalJob
        fields = '__all__'

    def to_representation(self, instance):
        evaljob = super().to_representation(instance)
        evaljob_id = evaljob['id']
        solution_id = evaljob['solution']
        adhoc_scenario_id = evaljob['adhoc_scenario']
        solution = AnalyticsSolution.objects.get(pk=solution_id)
        adhoc_scenario = Scenario.objects.filter(pk=adhoc_scenario_id)

        scenario_json = []
        # Get all Scenarios for Analytics Solution
        for scenario in solution.scenarios | adhoc_scenario:
            model_json = []
            # Get all Models for Analytics Solution
            for model in solution.models:
                ids_json, nodes_json = [], []
                # Get all Input Page Data Sets associated with Model and Scenario
                for ids in scenario.input_data_sets.filter(input_page__model=model):
                    ids_json.append(
                        GoogleCloudStorage.get_url(f'{ids.file}'))

                # Get all Node Overrides associated with Model and Scenario
                for node_override in scenario.node_overrides.filter(node__model=model):
                    nodes_json.append({
                        'id': node_override.node.tam_id,
                        'value': node_override.value,
                    })

                # Only add Model to json if it contains at least one IDS
                model_json.append({
                    'id': model.tam_id,
                    'input_data_sets': ids_json,
                    'nodes': nodes_json,
                })
            # Only add Scenario to json if it contains at least one Model with an IDS
            scenario_json.append({
                'name': scenario.name,
                'models': model_json
            })
        evaljob_json = {
            'analytics_job_id': evaljob_id,
            'tam_model_url': GoogleCloudStorage.get_url(f'{solution.tam_file}'),
            'time_start': evaljob['layer_time_start'],
            'time_increment_unit': evaljob['layer_time_increment'],
            'scenarios': scenario_json
        }
        return evaljob_json


class AnalyticsSolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsSolution
        fields = '__all__'


class NodeResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeResult
        fields = '__all__'


class NodeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeData
        fields = '__all__'


class InputNodeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = InputNodeData
        fields = '__all__'


class ConstNodeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstNodeData
        fields = '__all__'


class ScenarioNodeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioNodeData
        fields = '__all__'


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = '__all__'


class FilterCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterCategory
        fields = '__all__'


class FilterOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterOption
        fields = '__all__'


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = '__all__'
