from functools import wraps

import material.frontend.views as material
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from app.forms import CreateEvalJobForm
from app.models import ExecutiveView, EvalJob, NodeData, ScenarioNodeData, Node, Model, InputNodeData, ConstNodeData
from app.serializers import EvalJobSerializer, NodeResultSerializer, \
    NodeDataSerializer, ScenarioNodeDataSerializer, NodeSerializer, ModelSerializer, InputNodeDataSerializer, \
    ConstNodeDataSerializer


# region REST Framework Api
def validate_api(serializer_cls, many=False):
    def decorator(function):
        @wraps(function)
        def wrapper(request):
            serializer = serializer_cls(data=request.data, many=many)
            if serializer.is_valid():
                return function(request, serializer)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return wrapper

    return decorator


class EvalJobDefinitionViewSet(ModelViewSet):
    queryset = EvalJob.objects.all()
    serializer_class = EvalJobSerializer


class NodeResultView(APIView):
    """Create or update a node result."""

    @staticmethod
    @validate_api(NodeResultSerializer, many=True)
    def post(request, serializer):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, s):
        return Response([{"id": 2000, "email": "varsha@gmail.com", "name": "Varsha"}], status=status.HTTP_201_CREATED)


class NodeDataAPIView(generics.ListCreateAPIView):
    queryset = NodeData.objects.all()
    serializer_class = NodeDataSerializer


class ScenarioNodeDataAPIView(generics.ListCreateAPIView):
    queryset = ScenarioNodeData.objects.all()
    serializer_class = ScenarioNodeDataSerializer


class AllNodeDataByModelAPIView(generics.ListAPIView):
    def get(self, request, format=None, **kwargs):
        model = Model.objects.get(id=self.kwargs['model'])
        model_serializer = ModelSerializer(model);

        return Response({
            'model': model_serializer.data,
        })


class ModelAPIView(generics.ListAPIView):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer


class InputNodeDataAPIView(generics.ListAPIView):
    queryset = InputNodeData.objects.all()
    serializer_class = InputNodeDataSerializer


class ConstNodeDataAPIView(generics.ListAPIView):
    queryset = ConstNodeData.objects.all()
    serializer_class = ConstNodeDataSerializer


class InputNodeDataByNodeListAPIView(generics.ListAPIView):
    serializer_class = InputNodeDataSerializer

    def get_queryset(self):
        node = self.kwargs['node']
        return InputNodeData.objects.filter(node_id=node)


class ConstNodeDataByNodeListAPIView(generics.ListAPIView):
    serializer_class = ConstNodeDataSerializer

    def get_queryset(self):
        node = self.kwargs['node']
        return ConstNodeData.objects.filter(node_id=node)


class NodeByModelListAPIView(generics.ListAPIView):
    serializer_class = NodeSerializer

    def get_queryset(self):
        model = self.kwargs['model']
        return Node.objects.filter(model_id=model)
# endregion


# region Material Design
class EvalJobViewSet(material.ModelViewSet):
    model = EvalJob
    list_display = ('name', 'date_created', 'status')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ExecutiveViewViewSet(material.ModelViewSet):
    model = ExecutiveView
    list_display = ('name',)


# endregion


def render_executive(request, executiveview_id):
    executive_view = get_object_or_404(ExecutiveView, pk=executiveview_id)
    form = CreateEvalJobForm(executive_view=executive_view, data=request.POST or None)

    if form.is_valid():
        evaljob = form.save()
        if evaljob:
            return redirect(f'/app/eval-job/{evaljob.pk}/detail/')

    return render(request, 'app/executiveview.html', {
        'form': form,
        'exec_view': executive_view,
    })
