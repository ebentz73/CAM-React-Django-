from rest_framework_mongoengine import serializers

from .models import EvalJob, BaselineConfig, Scenario


class EvalJobSerializer(serializers.DocumentSerializer):
    class Meta:
        model = EvalJob
        fields = '__all__'


class BaselineConfigSerializer(serializers.DocumentSerializer):
    class Meta:
        model = BaselineConfig
        fields = '__all__'


class ScenarioSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Scenario
        fields = '__all__'
