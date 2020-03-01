from rest_framework import serializers

from app.models import NodeResult


class NodeResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeResult
        fields = '__all__'
