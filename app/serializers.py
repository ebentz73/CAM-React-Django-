from rest_framework import serializers

from app.models import AnalyticsSolution, EvalJob, NodeResult
from app.utils import GoogleCloudStorage


class EvalJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvalJob
        fields = '__all__'

    def to_representation(self, instance):
        evaljob = super().to_representation(instance)
        solution_id = evaljob['solution']
        solution = AnalyticsSolution.objects.get(pk=solution_id)

        input_data_sets = iter((
            GoogleCloudStorage.get_url('inputdatasets/low.xlsx'),
            GoogleCloudStorage.get_url('inputdatasets/mid.xlsx'),
            GoogleCloudStorage.get_url('inputdatasets/high.xlsx'),
        ))

        scenario_json = []
        for scenario in solution.scenarios:
            model_json = []
            for model in solution.models:
                model_json.append({
                    'name': model.name,
                    'input_data_sets': [next(input_data_sets)]  # TODO: CHANGE ME
                })
            scenario_json.append({
                'name': scenario.name,
                'models': model_json
            })

        evaljob_json = {
            'analytics_job_id': solution_id,
            'tam_model_url': GoogleCloudStorage.get_url(f'{solution.tam_file}'),
            'scenarios': scenario_json
        }
        return evaljob_json


class NodeResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeResult
        fields = '__all__'
