from django.shortcuts import render
from rest_framework import generics
from .serializers import (
    EvalJobSerializer,
    NodeDataSerializer,
    ScenarioNodeDataSerializer,
)
from .models import EvalJob, NodeData, ScenarioNodeData


def index(request):
    return render(request, "frontend/index.html")


class EvalJobAPIView(generics.ListCreateAPIView):
    queryset = EvalJob.objects.all()
    serializer_class = EvalJobSerializer


class NodeDataAPIView(generics.ListCreateAPIView):
    queryset = NodeData.objects.all()
    serializer_class = NodeDataSerializer


class ScenarioNodeDataAPIView(generics.ListCreateAPIView):
    queryset = ScenarioNodeData.objects.all()
    serializer_class = ScenarioNodeDataSerializer
