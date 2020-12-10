import csv
import json
import logging
from functools import wraps

import material.frontend.views as material
import datetime
import time
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from app.forms import CreateEvalJobForm
from app.models import (
    AnalyticsSolution,
    ConstNodeData,
    DecimalNodeOverride,
    EvalJob,
    ExecutiveView,
    FilterCategory,
    FilterOption,
    InputNodeData,
    Model,
    Node,
    NodeResult,
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
    ScenarioEvaluateSerializer,
)
from app.utils import PowerBI, run_eval_engine


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

    @action(detail=True)
    def report(self, request, pk):
        instance = self.get_object()
        powerbi = PowerBI(instance, request.user)
        try:
            return Response(powerbi.get_embed_token())
        except Exception as e:
            logging.error(e, exc_info=True)
            return Response({'errorMsg': str(e)}, 500)


class ScenarioViewSet(ModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer

    def create(self, request, solution_pk=None, **kwargs):
        run_eval = request.data.pop('run_eval', False)

        if 'solution' not in request.data:
            request.data['solution'] = solution_pk
        if 'shared' not in request.data:
            request.data['shared'] = []

        response = super().create(request, **kwargs)
        if run_eval:
            response.then = run_eval_engine
            response.then_args = (solution_pk, response.data['id'])

        return response

    def update(self, request, solution_pk, pk, **kwargs):
        run_eval = request.data.pop('run_eval', False)

        if 'solution' not in request.data:
            request.data['solution'] = solution_pk
        if 'shared' not in request.data:
            request.data['shared'] = []

        response = super().update(request, **kwargs)
        if run_eval:
            response.then = run_eval_engine
            response.then_args = (solution_pk, pk)

        return response

    @action(detail=True)
    def evaluate(self, request, solution_pk, pk):
        instance = self.get_object()
        serializer = ScenarioEvaluateSerializer(instance)
        return Response(serializer.data)

    @evaluate.mapping.patch
    def patch_evaluate(self, request, solution_pk, pk):
        return self.update(request, solution_pk, pk, partial=True)
        
    @action(detail=True, methods=['post'])
    def clone(self, request, solution_pk, pk):
        body = json.loads(request.body)
        clone = self.copy_scenario(pk, body['name'])
        serializer = ScenarioSerializer(clone)

        self.copy_scenario_data(ConstNodeData, pk, clone.pk)
        self.copy_scenario_data(InputNodeData, pk, clone.pk)
        self.copy_scenario_data(DecimalNodeOverride, pk, clone.pk)

        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def merge(self, request, solution_pk, pk):
        body = json.loads(request.body)
        clone = self.copy_scenario(pk, body['name'])
        serializer = ScenarioSerializer(clone)

        self.copy_scenario_data(ConstNodeData, pk, clone.pk)
        self.copy_scenario_data(InputNodeData, pk, clone.pk)
        self.copy_scenario_data(DecimalNodeOverride, pk, clone.pk)

        self.copy_scenario_data(ConstNodeData, body['mergeId'], clone.pk)
        self.copy_scenario_data(InputNodeData, body['mergeId'], clone.pk)
        self.copy_scenario_data(DecimalNodeOverride, body['mergeId'], clone.pk)

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def export(self, request, solution_pk, pk):
        scenario = Scenario.objects.get(Q(pk=pk))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{scenario.name}_results.csv"'

        writer = csv.writer(response)
        writer.writerow(['Scenario', 'Model', 'Node', 'Layer',
                         'Node Tags', 'Result 10', 'Result 30',
                         'Result 50', 'Result 70', 'Result 90'])
        node_results = NodeResult.objects.filter(Q(scenario_id=pk)).values_list('scenario', 'model', 'node', 'layer',
                                                                                'node_tags', 'result_10', 'result_30',
                                                                                'result_50', 'result_70', 'result_90')
        for node_result in node_results:
            writer.writerow(node_result)

        return response

    @action(detail=True, methods=['get'])
    def reset(self, request, solution_pk, pk):
        scenario = Scenario.objects.get(Q(pk=pk))
        scenario.status = None
        scenario.save()
        serializer = ScenarioSerializer(scenario)

        NodeResult.objects.filter(scenario_id=pk).delete()

        return Response(serializer.data)


    @staticmethod
    def copy_scenario(pk, name):
        clone = Scenario.objects.get(Q(pk=pk))
        clone.pk = None
        clone.name = name
        clone.save()
        return clone

    @staticmethod
    def copy_scenario_data(class_name, original_pk, clone_pk):
        class_node_data = class_name.objects.filter(Q(scenario_id=original_pk))
        duplicate_prevention_data = class_name.objects.filter(Q(scenario_id=clone_pk))

        for data in class_node_data:
            write_data = True
            for duplicate in duplicate_prevention_data:
                if data.node_id == duplicate.node_id:
                    write_data = False
                    break
            if write_data:
                data.id = None
                data.pk = None
                data.scenario_id = clone_pk
                data.save()


class ScenarioEvaluateViewSet(ModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioEvaluateSerializer


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


class ScenarioByIdAPIView(generics.ListCreateAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        return self.queryset.filter(id=self.kwargs.get('pk'))


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
        powerbi = PowerBI(solution, request.user)
        try:
            return Response(powerbi.get_embed_token())
        except Exception as e:
            logging.error(e, exc_info=True)
            return Response({'errorMsg': str(e)}, 500)


class AnalyticsSolutionScenarios(generics.ListAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        solution_id = self.kwargs.get('pk')
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
        solution = AnalyticsSolution.objects.get(id=request.data['solution'])
        if request.data['date']:
            date = datetime.datetime.strptime(request.data['date'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
        else:
            date = datetime.date.today()
        if 'scenario_id' in request.data:
            scenario = Scenario.objects.get(id=request.data['scenario_id'])
            data = {'name': request.data['name'], 'solution': request.data['solution'],
                    'is_adhoc': request.data['is_adhoc'], 'date': date}
            serializer = ScenarioSerializer(scenario, data=data)
            if serializer.is_valid():
                serializer.save()
        else:
            scenario = Scenario.objects.create(name=request.data['name'], solution=solution,
                                               date=date, is_adhoc=request.data['is_adhoc'])
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
                serializer = ConstNodeDataSerializer(const_node_data[0], data=data)

                if serializer.is_valid():
                    serializer.save()
            else:
                const_data = ConstNodeData.objects.create(node=node, scenario=scenario,
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
