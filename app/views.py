from functools import wraps

import material.frontend.views as material
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from app.forms import CreateEvalJobForm
from app.models import (
    AnalyticsSolution,
    ConstNodeData,
    EvalJob,
    ExecutiveView,
    FilterCategory,
    FilterOption,
    InputNodeData,
    Model,
    Node,
    Scenario,
)
from app.serializers import (
    AnalyticsSolutionSerializer,
    ConstNodeDataSerializer,
    EvalJobSerializer,
    FilterCategorySerializer,
    FilterOptionSerializer,
    InputNodeDataSerializer,
    ModelSerializer,
    NodeResultSerializer,
    NodeSerializer,
    ScenarioSerializer,
)
from app.utils import PowerBI

from profile.models import Role, UserProfile


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


class AnalyticsSolutionViewSet(ModelViewSet):
    queryset = AnalyticsSolution.objects.all()
    serializer_class = AnalyticsSolutionSerializer


class ScenarioViewSet(ModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer


class NodeResultView(APIView):
    """Create or update a node result."""

    @staticmethod
    @validate_api(NodeResultSerializer, many=True)
    def post(request, serializer):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class ScenarioAPIView(generics.ListCreateAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer


class FilterCategoriesAndOptionsBySolutionAPIView(generics.ListAPIView):
    def get(self, request, format=None, **kwargs):
        categories = FilterCategory.objects.filter(solution_id=self.kwargs['pk'])
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
        models = Model.objects.filter(solution_id=self.kwargs['pk'])
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


class PowerBIAPIView(APIView):
    queryset = AnalyticsSolution.objects.all()

    def get(self, request, *args, **kwargs):
        solution = AnalyticsSolution.objects.get(**kwargs)
        powerbi = PowerBI()
        return Response(powerbi.run(solution))


class AnalyticsSolutionScenarios(generics.ListAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        solution_id = self.kwargs.get('pk')
        print(solution_id, '------------------------')
        return self.queryset.filter(solution=solution_id)


class AllNodeDataBySolutionAPIView(generics.ListAPIView):
    def get(self, request, format=None, **kwargs):
        models = Model.objects.filter(solution_id=self.kwargs['pk'])
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


class CreateOrUpdateScenario(APIView):
    def post(self, request, format=None):
        print(request.data)
        scenarios = Scenario.objects.filter(id=request.data['scenario_id'])
        scenario_count = scenarios.count()
        serializer = None
        if scenario_count == 1:
            data = {'name': request.data['name'], 'solution': request.data['solution'], 'is_adhoc': request.data['is_adhoc']}
            serializer = ScenarioSerializer(scenarios[0], data=data)
            if serializer.is_valid():
                serializer.save()
        elif scenario_count == 0:
            scenario, _ = Scenario.objects.create(name=request.data['name'],
                                                  solution=request.data['solution'], is_adhoc=request.data['is_adhoc'])
            serializer = ScenarioSerializer(scenario)
        return Response(serializer.data)


class CreateOrUpdateNodeDataByScenario(APIView):
    def post(self, request, format=None):
        node = Node.objects.filter(id=request.data['node'])[0]
        scenario = Scenario.objects.filter(id=request.data['scenario_id'])[0]
        if request.data['type'] == 'input':
            input_node_data = InputNodeData.objects.filter(node=request.data['node'],
                                                           scenario=request.data['scenario_id'])
            if input_node_data.count() > 0:
                data = {'default_data': request.data['default_data']}
                serializer = InputNodeDataSerializer(input_node_data[0], data=data)

                if serializer.is_valid():
                    serializer.save()
            else:
                input_data = InputNodeData.objects.create(node=node, scenario=scenario,
                                                          default_data=request.data['default_data'], is_model=False, )
        if request.data['type'] == 'const':
            const_node_data = ConstNodeData.objects.filter(node=request.data['node'],
                                                           scenario=request.data['scenario_id'])
            if const_node_data.count() > 0:
                data = {'default_data': request.data['default_data']}
                serializer = ConstNodeDataSerializer(input_node_data[0], data=data)

                if serializer.is_valid():
                    serializer.save()
            else:
                const_data = InputNodeData.objects.create(node=node, scenario=scenario,
                                                          default_data=request.data['default_data'], is_model=False, )

        return Response(status=status.HTTP_201_CREATED)


class AllNodeDataByScenarioAPIView(generics.ListAPIView):
    def get(self, request, format=None, **kwargs):

        input_nodes = InputNodeData.objects.filter(scenario=self.kwargs['pk'])
        input_serializer = InputNodeDataSerializer(input_nodes, many=True)

        const_nodes = ConstNodeData.objects.filter(scenario=self.kwargs['pk'])
        const_serializer = ConstNodeDataSerializer(const_nodes, many=True)

        return Response({
            'input_nodes': input_serializer.data,
            'const_nodes': const_serializer.data
        })


class AllNodeDataByModelAPIView(generics.ListAPIView):
    def get(self, request, format=None, **kwargs):
        input_nodes = InputNodeData.objects.filter(scenario=None)
        input_serializer = InputNodeDataSerializer(input_nodes, many=True)

        const_nodes = ConstNodeData.objects.filter(scenario=None)
        const_serializer = ConstNodeDataSerializer(const_nodes, many=True)

        return Response({
            'input_nodes': input_serializer.data,
            'const_nodes': const_serializer.data
        })


class AnalyticsSolutionAPIView(generics.ListAPIView):
    queryset = AnalyticsSolution.objects.all()

    def get(self, request, format=None, **kwargs):
        if request.user.is_superuser:
            solutions = AnalyticsSolution.objects.all()
        else:
            profile = UserProfile.objects.get(user=request.user)
            solutions = AnalyticsSolution.objects.filter(role__in=profile.roles.all())

        serializer = AnalyticsSolutionSerializer(solutions, many=True)
        return Response(serializer.data)


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


class ScenariosBySolutionAPIView(generics.ListCreateAPIView):
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        return Scenario.objects.filter(solution=self.kwargs['pk'])


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
        solution = self.kwargs['pk']
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
