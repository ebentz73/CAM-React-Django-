from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_polymorphic import serializers as polymorphic_serializers

from app.models import (
    AnalyticsSolution,
    ConstNodeData,
    EvalJob,
    FilterCategory,
    FilterOption,
    Input,
    InputDataSet,
    InputDataSetInput,
    InputDataSetInputChoice,
    InputNodeData,
    Model,
    Node,
    NodeData,
    NumericInput,
    NodeResult,
    Scenario,
    SliderInput,
)
from app.utils import StorageHelper, is_cloud


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
                    ids_json.append(StorageHelper.get_url(f'{ids.file}'))

                # Get all Node Overrides associated with Model and Scenario
                for node_override in scenario.node_overrides.filter(node__model=model):
                    nodes_json.append(
                        {'id': node_override.node.tam_id, 'value': node_override.value}
                    )

                # Only add Model to json if it contains at least one IDS
                model_json.append(
                    {
                        'id': model.tam_id,
                        'input_data_sets': ids_json,
                        'nodes': nodes_json,
                    }
                )
            # Only add Scenario to json if it contains at least one Model with an IDS
            scenario_json.append({'name': scenario.name, 'models': model_json})

        # Get the hostname the eval engine will use to call Django
        callback_url = (
            f'https://{settings.AZ_CUSTOM_DOMAIN}'
            if is_cloud()
            else 'http://host.docker.internal:8000'
        )

        # Prepare schema to return to eval engine
        evaljob_json = {
            'analytics_job_id': evaljob_id,
            'tam_model_url': StorageHelper.get_url(str(solution.tam_file), expire=600),
            'results_url': f'{callback_url}/api/results/',
            'time_start': evaljob['layer_time_start'],
            'time_increment_unit': evaljob['layer_time_increment'],
            'scenarios': scenario_json,
        }
        return evaljob_json


def generic_serializer(cls, **kwargs):
    """Create a generic serializer for the given model."""
    fields_ = kwargs.pop('fields', '__all__')

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = cls
            fields = fields_

        for k, v in kwargs.items():
            setattr(Meta, k, v)

    return Serializer


AnalyticsSolutionSerializer = generic_serializer(AnalyticsSolution)
ConstNodeDataSerializer = generic_serializer(ConstNodeData)
FilterCategorySerializer = generic_serializer(FilterCategory, depth=1)
FilterOptionSerializer = generic_serializer(FilterOption)
InputSerializer = generic_serializer(Input)
InputDataSetSerializer = generic_serializer(InputDataSet)
InputDataSetInputChoiceSerializer = generic_serializer(InputDataSetInputChoice)
InputNodeDataSerializer = generic_serializer(InputNodeData)
ModelSerializer = generic_serializer(Model)
NodeSerializer = generic_serializer(Node)
NodeDataSerializer = generic_serializer(NodeData)
NodeResultSerializer = generic_serializer(NodeResult)
NumericInputSerializer = generic_serializer(
    NumericInput, fields=('id', 'name', 'solution', 'node'),
)
SliderInputSerializer = generic_serializer(
    SliderInput,
    fields=('id', 'name', 'solution', 'node', 'minimum', 'maximum', 'step'),
)


class InputDataSetInputSerializer(serializers.ModelSerializer):
    choices = InputDataSetInputChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = InputDataSetInput
        fields = ('id', 'name', 'solution', 'choices')


class PolyInputSerializer(polymorphic_serializers.PolymorphicSerializer):
    model_serializer_mapping = {
        Input: InputSerializer,
        InputDataSetInput: InputDataSetInputSerializer,
        NumericInput: NumericInputSerializer,
        SliderInput: SliderInputSerializer,
    }


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()  # implicitly-generated ``id`` field is read-only

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class ScenarioSerializer(serializers.ModelSerializer):
    shared = UserSerializer(many=True)

    class Meta:
        model = Scenario
        fields = (
            'id',
            'shared',
            'name',
            'is_in_progress',
            'status',
            'layer_date_start',
            'solution',
            'input_data_sets',
        )

    @staticmethod
    def add_shared(instance, shared):
        for user_data in shared:
            user = User.objects.get(pk=user_data.get('id'))
            instance.shared.add(user)

    @staticmethod
    def add_input_data_sets(instance, input_data_sets):
        for ids_id in input_data_sets:
            ids = InputDataSet.objects.get(pk=ids_id)
            instance.input_data_sets.add(ids)

    def create_or_update(self, validated_data, instance=None):
        shared = validated_data.pop('shared', [])
        instance = (
            super().create(validated_data)
            if instance is None
            else super().update(instance, validated_data)
        )
        self.add_shared(instance, shared)
        return instance

    def create(self, validated_data):
        return self.create_or_update(validated_data)

    def update(self, instance, validated_data):
        return self.create_or_update(validated_data, instance)


class FilterCategoryOptionsSerializer(serializers.ModelSerializer):
    filteroption_set = FilterOptionSerializer(many=True, read_only=True)

    class Meta:
        model = FilterCategory
        fields = '__all__'


class PolyNodeDataSerializer(polymorphic_serializers.PolymorphicSerializer):
    model_serializer_mapping = {
        NodeData: NodeDataSerializer,
        InputNodeData: InputNodeDataSerializer,
        ConstNodeData: ConstNodeDataSerializer
    }


class ScenarioEvaluateSerializer(serializers.ModelSerializer):
    tam_model_url = serializers.SerializerMethodField()
    results_url = serializers.SerializerMethodField()
    time_start = serializers.ReadOnlyField(source='layer_date_start')
    time_increment_unit = serializers.ReadOnlyField(
        source='solution.layer_time_increment'
    )
    scenario = serializers.SerializerMethodField()

    class Meta:
        model = Scenario
        fields = (
            'tam_model_url',
            'results_url',
            'time_start',
            'time_increment_unit',
            'scenario',
        )

    @staticmethod
    def get_tam_model_url(obj: Scenario):
        return StorageHelper.get_url(str(obj.solution.tam_file), expire=600)

    @staticmethod
    def get_results_url(_):
        # Get the hostname the eval engine will use to call Django
        callback_url = (
            f'https://{settings.AZ_CUSTOM_DOMAIN}'
            if is_cloud()
            else 'http://host.docker.internal:8000'
        )
        return f'{callback_url}/api/results/'

    @staticmethod
    def get_scenario(obj: Scenario):
        model_json = []
        for model in obj.solution.models:
            nodes_json = list(
                map(
                    lambda node_data: {
                        'id': node_data.node.tam_id,
                        'value': node_data.default_data,
                    },
                    obj.node_data.filter(node__model=model),
                )
            )
            model_json.append(
                {'id': model.tam_id, 'input_data_sets': [], 'nodes': nodes_json,}
            )
        return {
            'pk': obj.pk,
            'name': obj.name,
            'models': model_json,
        }
