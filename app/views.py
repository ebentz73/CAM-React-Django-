import csv
import datetime
import logging
import requests
from functools import wraps

import material.frontend.views as material
from django.db.models import Q
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from profile.models import UserProfile
from rest_framework import generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_guardian.filters import ObjectPermissionsFilter


from app.mixins import NestedViewSetMixin
from app.models import (
    AnalyticsSolution,
    ConstNodeData,
    DecimalNodeOverride,
    EvalJob,
    FilterCategory,
    FilterOption,
    Input,
    InputNodeData,
    Model,
    Node,
    NodeData,
    NodeResult,
    Scenario,
    InputDataSet,
    InputDataSetInputChoice,
)
from app.permissions import CustomObjectPermissions
from app.serializers import (
    AnalyticsSolutionSerializer,
    ConstNodeDataSerializer,
    FilterCategorySerializer,
    FilterOptionSerializer,
    InputNodeDataSerializer,
    ModelSerializer,
    NodeResultSerializer,
    NodeSerializer,
    PolyInputSerializer,
    ScenarioSerializer,
    ScenarioEvaluateSerializer,
    FilterCategoryOptionsSerializer,
    PolyNodeDataSerializer,
    InputDataSetSerializer,
    UserSerializer,
)
from app.utils import PowerBI, run_eval_engine, assign_model_perm


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


def catch_request_exception(f):
    """
    Catch a `requests` exception and add the Microsoft error message, if it
    exists.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            return result
        except requests.exceptions.RequestException as e:
            try:
                body = e.response.json()
            except ValueError:
                # Response does not contain valid json
                body = {}
            msg = f"{e}: {body['error']['message']}" if 'error' in body else str(e)
            logging.error(msg)
            return Response({'errorMsg', msg}, 500)
    return wrapper


class NodeViewSet(ModelViewSet):
    serializer_class = NodeSerializer
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    filter_backends = (ObjectPermissionsFilter,)

    def get_queryset(self):
        if 'model_pk' in self.kwargs:
            return Node.objects.filter(model=self.kwargs['model_pk'])
        else:
            return Node.objects.filter(model__solution=self.kwargs['solution_pk'])


class FilterCategoryViewSet(ModelViewSet):
    serializer_class = FilterCategoryOptionsSerializer
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    filter_backends = (ObjectPermissionsFilter,)

    def get_queryset(self):
        return FilterCategory.objects.filter(solution=self.kwargs['solution_pk'])


class FilterOptionViewSet(ModelViewSet):
    serializer_class = FilterOptionSerializer
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    filter_backends = (ObjectPermissionsFilter,)

    def get_queryset(self):
        return FilterOption.objects.filter(category=self.kwargs['filtercategory_pk'])


class AnalyticsModelViewSet(ModelViewSet):
    serializer_class = ModelSerializer
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    filter_backends = (ObjectPermissionsFilter,)

    def get_queryset(self):
        return Model.objects.filter(solution=self.kwargs['solution_pk'])


class AnalyticsSolutionViewSet(ModelViewSet):
    queryset = AnalyticsSolution.objects.all()
    serializer_class = AnalyticsSolutionSerializer
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    filter_backends = (ObjectPermissionsFilter,)

    @catch_request_exception
    @action(detail=True, url_path='powerbi/token')
    def token(self, request, pk):
        instance = self.get_object()
        powerbi = PowerBI(instance, request.user)
        return Response(powerbi.get_embed_token())

    @catch_request_exception
    @action(detail=True, url_path='powerbi/refresh')
    def refresh(self, request, pk):
        instance = self.get_object()
        powerbi = PowerBI(instance, request.user)
        powerbi.refresh_dataset()
        return Response('Success.')


class InputViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = Input.objects.all()
    serializer_class = PolyInputSerializer
    parent_lookup_kwargs = {'solution_pk': 'solution'}


class InputNodeDataViewSet(ModelViewSet):
    serializer_class = InputNodeDataSerializer
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    filter_backends = (ObjectPermissionsFilter,)

    def get_queryset(self):
        if 'scenario_pk' in self.kwargs:
            return InputNodeData.objects.filter(scenario=self.kwargs['scenario_pk'])
        else:
            return InputNodeData.objects.filter(node=self.kwargs['node_pk'])


class ConstNodeDataViewSet(ModelViewSet):
    serializer_class = ConstNodeDataSerializer
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    filter_backends = (ObjectPermissionsFilter,)

    def get_queryset(self):
        if 'scenario_pk' in self.kwargs:
            return ConstNodeData.objects.filter(scenario=self.kwargs['scenario_pk'])
        else:
            return ConstNodeData.objects.filter(node=self.kwargs['node_pk'])


class ScenarioViewSet(ModelViewSet):
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        return Scenario.objects.filter(solution=self.kwargs['solution_pk'])

    def create_or_update(self, request, solution_pk=None, pk=None, **kwargs):
        # _mutable = request.data._mutable
        # request.data._mutable = True

        run_eval = request.data.pop('run_eval', False)
        if 'solution' not in request.data:
            request.data['solution'] = solution_pk
        if 'shared' not in request.data:
            request.data['shared'] = []

        # request.data._mutable = _mutable

        meth = super().create if pk is None else super().update
        response = meth(request, **kwargs)

        if run_eval:
            response.then = run_eval_engine
            response.then_args = (solution_pk, pk or response.data['id'])

        return response
    update = create_or_update

    def create(self, request, solution_pk=None, **kwargs):
        response = self.create_or_update(request, solution_pk, **kwargs)
        obj = Scenario.objects.get(pk=response.data['id'])
        assign_model_perm(request.user, obj)
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
        body = request.data
        clone = self.copy_scenario(pk, body['name'])
        serializer = ScenarioSerializer(clone)

        self.copy_scenario_data(ConstNodeData, pk, clone.pk)
        self.copy_scenario_data(InputNodeData, pk, clone.pk)
        self.copy_scenario_data(DecimalNodeOverride, pk, clone.pk)

        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def merge(self, request, solution_pk, pk):
        body = request.data
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
        scenario.status = 'Unevaluated'
        scenario.save()
        serializer = ScenarioSerializer(scenario)

        PowerBI(scenario.solution).refresh_dataset()

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


class InputDataSetViewSet(ModelViewSet):
    queryset = InputDataSet.objects.all()
    serializer_class = InputDataSetSerializer

    def get_queryset(self):
        return InputDataSet.objects.filter(
            inputdatasetinputchoice__in=InputDataSetInputChoice.objects.filter(
                input__solution=self.kwargs['solution_pk'])
        )


class ScenarioNodeDataViewSet(ModelViewSet):
    serializer_class = PolyNodeDataSerializer

    def get_queryset(self):
        return NodeData.objects.filter(scenario=self.kwargs['solution_pk'], is_model=True)


class NodeDataViewSet(ModelViewSet):
    serializer_class = PolyNodeDataSerializer

    def get_queryset(self):
        if 'inputdataset_pk' in self.kwargs:
            return NodeData.objects.filter(input_data_set=self.kwargs['inputdataset_pk'])
        elif 'scenario_pk' in self.kwargs:
            return NodeData.objects.filter(scenario=self.kwargs['scenario_pk'])
        else:
            return NodeData.objects.filter(node__model__solution=self.kwargs['solution_pk'], is_model=True)


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


class EvalJobViewSet(material.ModelViewSet):
    model = EvalJob
    list_display = ('name', 'date_created', 'status')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class UserAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
