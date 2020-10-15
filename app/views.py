from functools import wraps

import material.frontend.views as material
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from app.forms import CreateEvalJobForm
from app.models import ExecutiveView, EvalJob, NodeData, ScenarioNodeData, Node, Model, \
    InputNodeData, ConstNodeData, AnalyticsSolution, FilterOption, FilterCategory, Scenario
from app.serializers import EvalJobSerializer, NodeResultSerializer, AnalyticsSolutionSerializer, \
    NodeDataSerializer, ScenarioNodeDataSerializer, NodeSerializer, ModelSerializer, \
    FilterCategorySerializer, FilterOptionSerializer, InputNodeDataSerializer, \
    ConstNodeDataSerializer, ScenarioSerializer


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


@method_decorator(csrf_exempt, name='dispatch')
class ScenarioAPIView(generics.ListCreateAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer


class NodeDataAPIView(generics.ListCreateAPIView):
    queryset = NodeData.objects.all()
    serializer_class = NodeDataSerializer


class ScenarioNodeDataBySolutionAPIView(generics.ListCreateAPIView):
    serializer_class = ScenarioNodeDataSerializer

    def get_queryset(self):
        solution = self.kwargs['solution']
        scenario_ids = [scenario.id for scenario in Scenario.objects.filter(solution=solution)]
        return ScenarioNodeData.objects.filter(scenario__in=scenario_ids)


@method_decorator(csrf_exempt, name='dispatch')
class ScenarioNodeDataAPIView(generics.ListCreateAPIView):
    queryset = ScenarioNodeData.objects.all()
    serializer_class = ScenarioNodeDataSerializer


class FilterCategoriesAndOptionsBySolutionAPIView(generics.ListAPIView):
    def get(self, request, format=None, **kwargs):
        categories = FilterCategory.objects.filter(solution_id=self.kwargs['solution'])
        categories_serializer = FilterCategorySerializer(categories, many=True)
        category_ids = [category.id for category in categories]
        options = FilterOption.objects.filter(category_id__in=category_ids)
        options_serializer = FilterOptionSerializer(options, many=True)

        return Response({
            'categories': categories_serializer.data,
            'options': options_serializer.data
        })


class ModelNodeDataBySolutionAPIView(generics.ListAPIView):
    def get(self, request, format=None, **kwargs):
        models = Model.objects.filter(solution_id=self.kwargs['solution'])
        model_ids = [model.id for model in models]
        nodes = Node.objects.filter(model_id__in=model_ids)
        node_ids = [node.id for node in nodes]

        input_nodes = InputNodeData.objects.filter(node_id__in=node_ids, is_model=True)
        input_serializer = InputNodeDataSerializer(input_nodes, many=True)

        const_nodes = ConstNodeData.objects.filter(node_id__in=node_ids, is_model=True)
        const_serializer = ConstNodeDataSerializer(const_nodes, many=True)

        nodes_serializer = NodeSerializer(nodes, many=True)

        return Response({
            'input_nodes': input_serializer.data,
            'const_nodes': const_serializer.data
        })


class AllNodeDataBySolutionAPIView(generics.ListAPIView):
    def get(self, request, format=None, **kwargs):
        models = Model.objects.filter(solution_id=self.kwargs['solution'])
        model_ids = [model.id for model in models]
        nodes = Node.objects.filter(model_id__in=model_ids)
        node_ids = [node.id for node in nodes]

        input_nodes = InputNodeData.objects.filter(node_id__in=node_ids)
        input_serializer = InputNodeDataSerializer(input_nodes, many=True)

        const_nodes = ConstNodeData.objects.filter(node_id__in=node_ids)
        const_serializer = ConstNodeDataSerializer(const_nodes, many=True)

        nodes_serializer = NodeSerializer(nodes, many=True)

        return Response({
            'input_nodes': input_serializer.data,
            'const_nodes': const_serializer.data
        })


class AllNodeDataByModelAPIView(generics.ListAPIView):
    def get(self, request, format=None, **kwargs):
        model = Model.objects.get(id=self.kwargs['model'])
        model_serializer = ModelSerializer(model)
        nodes = Node.objects.filter(model_id=self.kwargs['model'])
        node_ids = [node.id for node in nodes]

        input_nodes = InputNodeData.objects.filter(node_id__in=node_ids)
        input_serializer = InputNodeDataSerializer(input_nodes, many=True)

        const_nodes = ConstNodeData.objects.filter(node_id__in=node_ids)
        const_serializer = ConstNodeDataSerializer(const_nodes, many=True)

        nodes_serializer = NodeSerializer(nodes, many=True)

        return Response({
            'input_nodes': input_serializer.data,
            'const_nodes': const_serializer.data
        })


class AnalyticsSolutionAPIView(generics.ListAPIView):
    queryset = AnalyticsSolution.objects.all()
    serializer_class = AnalyticsSolutionSerializer


class ModelAPIView(generics.ListAPIView):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer


@method_decorator(csrf_exempt, name='dispatch')
class InputNodeDataAPIView(generics.ListCreateAPIView):
    queryset = InputNodeData.objects.all()
    serializer_class = InputNodeDataSerializer


@method_decorator(csrf_exempt, name='dispatch')
class ConstNodeDataAPIView(generics.ListCreateAPIView):
    queryset = ConstNodeData.objects.all()
    serializer_class = ConstNodeDataSerializer


class InputNodeDataByNodeListAPIView(generics.ListCreateAPIView):
    serializer_class = InputNodeDataSerializer

    def get_queryset(self):
        node = self.kwargs['node']
        return InputNodeData.objects.filter(node_id=node)


class ConstNodeDataByNodeListAPIView(generics.ListAPIView):
    serializer_class = ConstNodeDataSerializer

    def get_queryset(self):
        node = self.kwargs['node']
        return ConstNodeData.objects.filter(node_id=node)


class NodeBySolutionListAPIView(generics.ListAPIView):
    serializer_class = NodeSerializer

    def get_queryset(self):
        solution = self.kwargs['solution']
        model_ids = [model.id for model in Model.objects.filter(solution_id=solution)]
        return Node.objects.filter(model_id__in=model_ids)


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
