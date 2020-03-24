from rest_framework import serializers

from app.models import AnalyticsSolution, EvalJob, NodeResult, Scenario
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
                ids_json = []
                # Get all Input Page Data Sets associated with Model and Scenario
                for ids in scenario.input_data_sets.filter(input_page__model=model):
                    ids_json.append(
                        GoogleCloudStorage.get_url(f'{ids.file}'))
                # Only add Model to json if it contains at least one IDS
                if ids_json:
                    model_json.append({
                        'name': model.name,
                        'input_data_sets': ids_json
                    })
            # Only add Scenario to json if it contains at least one Model with an IDS
            if any(x['input_data_sets'] for x in model_json):
                scenario_json.append({
                    'name': scenario.name,
                    'models': model_json
                })
        evaljob_json = {
            'analytics_job_id': evaljob_id,
            'tam_model_url': GoogleCloudStorage.get_url(f'{solution.tam_file}'),
            'scenarios': scenario_json
        }
        return evaljob_json


class NodeResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeResult
        fields = '__all__'
