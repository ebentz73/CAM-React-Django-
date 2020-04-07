from functools import wraps

import material.frontend.views as material
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.defaulttags import register
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from app.forms import CreateEvalJobForm
from app.models import Model, ExecutiveView, InputDataSet, EvalJob, NodeResult
from app.serializers import EvalJobSerializer, NodeResultSerializer


def validate_api(serializer_cls):
    def decorator(function):
        @wraps(function)
        def wrapper(request):
            serializer = serializer_cls(data=request.data)
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
    @validate_api(NodeResultSerializer)
    def post(request, serializer):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def stop(request, evaljob_id):
    # Update the status of the eval job
    evaljob = get_object_or_404(EvalJob, pk=evaljob_id)
    evaljob.status = 'Stopped.'
    # TODO: If running a VM, stop it

    return render(request, 'app/index.html')


# Load Datasets for the executive views
def load_ds(request):
    inputpage_id = request.GET.get('page')
    data_sets = InputDataSet.objects.filter(input_page=inputpage_id)
    return render(request, 'app/hr/dropdown_test_view.html', {'data_sets': data_sets})


# Render_executive view
def render_executive(request, executiveview_id):
    instance = get_object_or_404(ExecutiveView, pk=executiveview_id)
    if request.method == 'POST':
        form = CreateEvalJobForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = CreateEvalJobForm(instance=instance)

    return render(request, 'app/ev.html', {'form': form, 'exec_view': instance})


# Create JSON and View Charts
def load_chart(request, evaljob_id):
    definition = NodeResult.objects.filter(eval_job=evaljob_id).values()
    scenarios = {}
    for qs in definition:
        temp = scenarios.get(qs['scenario'], {})
        temp_node = temp.get(qs['node'], [])
        temp_layer = {
            'name': qs['layer'],
            'result_10': qs['result_10'],
            'result_30': qs['result_30'],
            'result_50': qs['result_50'],
            'result_70': qs['result_70'],
            'result_90': qs['result_90']
        }
        temp_node.append(temp_layer)
        temp[qs['node']] = temp_node
        scenarios[qs['scenario']] = temp
    json_1 = []
    for key, value in scenarios.items():
        temp_scn = {}
        temp_scn["name"] = key
        temp_val = []
        for x, y in value.items():
            temp_val2 = {}
            temp_val2["name"] = x
            temp_val2["layers"] = y
            temp_val.append(temp_val2)
        temp_scn["nodes"] = temp_val
        json_1.append(temp_scn)

    json_data = {"scenarios": json_1}
    # print(json_data)
    # print(json_data)
    context = {'json_data': json_data, 'scenario_num': len(scenarios)}
    return render(request, 'app/highcharts.html', context)


# Pass Models as data to Executive View Change Form
def change_view(request):
    models = Model.objects.all().values_list('name')
    return render(request, 'app/change_form_update.html', {'models': models})


def search_ds(request):
    if request.method == "POST":
        search_ds = request.POST['data']
        print(search_ds)


class EvalJobViewSet(material.ModelViewSet):
    model = EvalJob
    form_class = CreateEvalJobForm


class ExecutiveViewViewSet(material.ModelViewSet):
    model = ExecutiveView
    list_display = ('name',)
