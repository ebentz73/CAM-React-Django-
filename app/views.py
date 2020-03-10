import json

from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import ExecutiveView
from app.models import InputDataSet, Scenario, Input, EvalJob, InputPage, NodeResult
from app.serializers import NodeResultSerializer
from app.utils import run_playbook
from .models import AnalyticsSolution, Model


class NodeResultView(APIView):

    @staticmethod
    def post(request):
        print(request.data)
        serializer = NodeResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def index(request):
    ex = ExecutiveView.objects.get(pk=1)
    return render(request, 'app/index.html', {'exec_view': ex})


def start(request):
    run_playbook(tags='gcp', extra_vars={'run_id': 1}, playbook='create-instance.yaml')
    return render(request, 'index.html')


def stop(request):
    run_playbook(tags='gcp', extra_vars={'run_id': 1}, playbook='delete-instance.yaml')
    return render(request, 'index.html')


# Load Datasets for the executive views
def load_ds(request):
    inputpage_id = request.GET.get('page')
    data_sets = InputDataSet.objects.filter(input_page=inputpage_id)
    return render(request, 'app/hr/dropdown_test_view.html', {'data_sets': data_sets})


# Render_executive view
def render_executive(request, executiveview_id, scenario_id, model_id):
    executive = ExecutiveView.objects.get(id=executiveview_id)
    url = AnalyticsSolution.objects.filter(id=executive.solution_id).values_list('file_url')
    scenario = Scenario.objects.filter(id=scenario_id).values_list('name')
    model = Model.objects.filter(id=model_id).values_list('name')
    inputs = Input.objects.filter(exec_view=executive)
    input_ds = InputDataSet.objects.all()

    definition = {"analytics_job_id": executive.solution_id,
                  "tam_model_url": url[0][0],
                  "scenarios": [{
                      "name": scenario[0][0],
                      "models": [
                          {
                              "name": model[0][0]
                          }
                      ]
                  }]}
    context = {'executive': executiveview_id, 'inputs': inputs, 'inputds': input_ds, 'definition': definition}
    return render(request, 'app/render_executive.html', context)


# Create JSON and View Charts
def load_chart(request, evaljob_id):
    definition = NodeResult.objects.filter(eval_job=evaljob_id).values()
    scenarios = {}
    for qs in definition:
        temp = scenarios.get(qs['scenario'], {})
        temp_node = temp.get(qs['node'], [])
        temp_layer = {}
        temp_layer['name'] = qs['layer']
        temp_layer['result_10'] = qs['result_10']
        temp_layer['result_30'] = qs['result_30']
        temp_layer['result_50'] = qs['result_50']
        temp_layer['result_70'] = qs['result_70']
        temp_layer['result_90'] = qs['result_90']
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
    context = {'json_data': json_data, 'scenario_num': len(scenarios)}
    return render(request, 'app/highcharts.html', context)


# Update Eval Job table from Executive View
@csrf_exempt
def update(request, pk):
    obj = ExecutiveView.objects.filter(id=pk).values_list('id', 'solution_id')
    exec_id = obj[0][0]
    sol_id = obj[0][1]
    if request.method == "POST" and request.is_ajax():
        receive_data = request.POST['someVar']
        receive_data = json.loads(receive_data)
        exec_name = request.POST.get('name', False)
        print(exec_name)
        temp_eval = EvalJob(definition=receive_data, DateCreated=timezone.now(), Status="Pending", solution_id=sol_id,
                            name=exec_name)
        temp_eval.save()
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
        input_pg = InputPage.objects.filter(model=model.first()).values_list('id', 'name')
        input_ds = []
        for i in input_pg:
            temp = InputDataSet.objects.filter(input_page=i[0]).values_list('id', 'name')
            input_ds.append(temp)
        model_temp = []
        for i in model:
            temp1 = {}
            temp1["name"] = i[1]
            temp1["input_data_sets"] = [j[1] for j in input_ds[0]]
            model_temp.append(temp1)
        solution["scenarios"] = []

        for i in scenario:
            temp2 = {}
            temp2["name"] = i[1]
            temp2["models"] = []
            temp2["models"].extend(model_temp)
            solution["scenarios"].append(temp2)
        print(solution)
        temp_eval = EvalJob(definition=solution, DateCreated=timezone.now(), Status="Pending", solution_id=object_id)
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
