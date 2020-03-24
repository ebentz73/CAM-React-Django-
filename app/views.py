import json
from collections import defaultdict

import docker
import environ
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.defaulttags import register
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from app.models import AnalyticsSolution, Model, ExecutiveView, InputDataSet, Scenario, Input, EvalJob, InputPage, \
    NodeResult, InputChoice
from app.serializers import EvalJobSerializer, NodeResultSerializer


class EvalJobDefinitionViewSet(ModelViewSet):
    queryset = EvalJob.objects.all()
    serializer_class = EvalJobSerializer


class NodeResultView(APIView):

    @staticmethod
    def post(request):
        serializer = NodeResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def start(solution: AnalyticsSolution, evaljob_id: int):
    env = environ.Env()

    # Run eval engine docker container for eval job
    client = docker.APIClient(base_url='tcp://localhost:2375')
    container = client.create_container('trunavconsolecore:latest',
                                        detach=True,
                                        environment={
                                            'EVALJOBDEF_URL': f'http://host.docker.internal:8000/api/evaljob/{evaljob_id}',
                                            'RESULTS_URL': 'http://host.docker.internal:8000/api/results/',
                                            'GOOGLE_APPLICATION_CREDENTIALS': '/credentials.json'},
                                        volumes=['/credentials.json'],
                                        host_config=client.create_host_config(
                                            binds=[
                                                f"{env('GOOGLE_APPLICATION_CREDENTIALS')}:/credentials.json"
                                            ]
                                        ))
    client.start(container)


def stop(request, evaljob_id):
    # Update the status of the eval job
    try:
        evaljob = EvalJob.objects.get(pk=evaljob_id)
        evaljob.status = 'Stopped.'
        # TODO: If running a VM, stop it
    except EvalJob.DoesNotExist:
        # TODO: Notify that eval job does not exist
        pass

    return render(request, 'index.html')


# Load Datasets for the executive views
def load_ds(request):
    inputpage_id = request.GET.get('page')
    data_sets = InputDataSet.objects.filter(input_page=inputpage_id)
    return render(request, 'app/hr/dropdown_test_view.html', {'data_sets': data_sets})


# Render_executive view
def render_executive(request, executiveview_id):
    exec_view = ExecutiveView.objects.get(id=executiveview_id)
    scenarios = Scenario.objects.filter(solution=exec_view.solution, is_adhoc=False)
    inputs = Input.objects.filter(exec_view=exec_view)
    input_ds = defaultdict(list)
    for inp in inputs:
        input_choices = InputChoice.objects.filter(input_id=inp.id)
        for input_choice in input_choices:
            input_ds[inp.id].append((input_choice.ids_id, input_choice.ids.name))
    context = {'executive': executiveview_id, 'inputs': inputs, 'inputds': input_ds, 'Scenarios': scenarios}
    return render(request, 'app/render_executive.html', context)


# Create JSON and View Charts
def load_chart(request, evaljob_id):
    client = docker.APIClient(base_url='tcp://localhost:2375')
    volumes = [
        '/eval_job_definition.json',
        '/tammy.tam',
        '/low.xlsx',
        '/mid.xlsx',
        '/high.xlsx'
    ]
    volume_bindings = [
        '/c/Development/trunavcore/files/eval_job_definition.json:/eval_job_definition.json',
        '/c/Development/trunavcore/files/tam_model.tam:/tammy.tam',
        '/c/Development/trunavcore/files/low.xlsx:/low.xlsx',
        '/c/Development/trunavcore/files/high.xlsx:/high.xlsx',
        '/c/Development/trunavcore/files/mid.xlsx:/mid.xlsx',
    ]
    container = client.create_container('trunavconsolecore:latest',
                                        detach=True,
                                        volumes=volumes,
                                        host_config=client.create_host_config(binds=volume_bindings,
                                                                              network_mode='host'))
    client.start(container)

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


# Update Eval Job table from Executive View
@csrf_exempt
def update(request, exec_view_id):
    if request.method == 'POST' and request.is_ajax():
        scenario_name = request.POST.get('scenario')
        selected_scenario_id = request.POST.get('sel_scenario')
        evaljob_name = request.POST.get('name')
        inputs = json.loads(request.POST.get('input'))

        exec_view = ExecutiveView.objects.get(pk=exec_view_id)
        selected_scenario = Scenario.objects.get(pk=selected_scenario_id)

        # Create Ad Hoc Scenario
        scenario = Scenario.objects.create(
            solution=exec_view.solution,
            name=scenario_name,
            is_adhoc=True,
        )

        # Validate inputs
        selected_input_pages = set()
        for ids in selected_scenario.input_data_sets:
            selected_input_pages.add(ids.input_page.id)

        seen_input_pages = set()
        for ids_id in inputs.values():
            ids = InputDataSet.objects.get(pk=ids_id)
            if ids.input_page.id not in seen_input_pages:
                ids.scenarios.add(scenario)
                seen_input_pages.add(ids.input_page.id)
            else:
                raise Exception('Cannot have multiple input data sets for a single input page.')

        for ids in selected_scenario.input_data_sets:
            if ids.input_page.id not in seen_input_pages:
                ids.scenarios.add(scenario)
                seen_input_pages.add(ids.input_page.id)

        # Create Eval Job
        evaljob = EvalJob.objects.create(
            solution=exec_view.solution,
            date_created=timezone.now(),
            status='Running.',
            name=evaljob_name,
            adhoc_scenario=scenario,
        )

        if selected_input_pages == seen_input_pages:
            start(exec_view.solution, evaljob.id)
        else:
            raise Exception('Input pages on modified scenario and ad hoc scenario do not match.')
    return redirect('/')


# Create EvalJob from Analytics Solution View and update Table
@csrf_exempt
def create_json(request, pk):
    if request.method == "POST" and request.is_ajax():
        object_id = request.POST['solution_id']
        solution = {"analytics_job_id": object_id,
                    "tam_model_url": AnalyticsSolution.objects.filter(id=object_id).values_list('file_url')[0][0],
                    "scenarios": []}
        scenario = Scenario.objects.filter(solution=object_id).values_list('id', 'name')
        model = Model.objects.filter(solution=object_id).values_list('id', 'name')
        for i in scenario:
            temp_scenario = {}
            temp_scenario["name"] = i[1]
            temp_scenario["models"] = []
            for j in model:
                temp_model = {}
                temp_model["name"] = j[1]
                temp_model["input_data_sets"] = []
                input_dataset_list = InputPageDsAsc.objects.filter(scenario=i[0]).values_list('ids_id', 'inputPage_id')
                for k in input_dataset_list:
                    if InputPage.objects.filter(id=k[1]).values_list('model', flat=True)[0] == j[0]:
                        temp_model["input_data_sets"].append(
                            InputDataSet.objects.filter(id=k[0]).values_list('name', flat=True)[0])
                temp_scenario["models"].append(temp_model)
            solution["scenarios"].append(temp_scenario)
        temp_eval = EvalJob(definition=solution, date_created=timezone.now(), status="Pending", solution_id=object_id,
                            source=1)
        temp_eval.save()
        t = EvalJob.objects.get(id=temp_eval.id)
        t.name = "EvalJob_" + str(temp_eval.id)
        t.save()
        return redirect('/')


# Pass Models as data to Executive View Change Form
def change_view(request):
    models = Model.objects.all().values_list('name')
    return render(request, 'app/change_form_update.html', {'models': models})


def search_ds(request):
    if request.method == "POST":
        search_ds = request.POST['data']
        print(search_ds)
