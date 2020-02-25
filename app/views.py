from .models import AnalyticsSolution, Model
from app.models import ExecutiveView, InputDataSet
#from app.utils import run_playbook
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View

'''
def index(request):
    ex = ExecutiveView.objects.get(pk=1)
    return render(request, 'app/index.html', {'exec_view': ex})
'''

def start(request):
    #run_playbook(tags='gcp', extra_vars={'run_id': 1}, playbook='create-instance.yaml')
    return render(request, 'index.html')


def stop(request):
    #run_playbook(tags='gcp', extra_vars={'run_id': 1}, playbook='delete-instance.yaml')
    return render(request, 'index.html')


def load_ds(request):
    inputpage_id = request.GET.get('country')
    data_sets = InputDataSet.objects.filter(input_page=inputpage_id)
    #data_sets = [{"pk":"1", "name":"a"}, {"pk":"2", "name":"b"}]
    return render(request, 'app/hr/dropdown_test_view.html', {'data_sets': data_sets})


def render_executive(request):
    scenarios = request.GET.get('scenarios')
    return render(request, 'app/render_executive.html',{'scenarios': scenarios})


def change_view(request):
    print("Executing*************")
    models = Model.objects.all().values_list('name')
    return render(request, 'app/change_view.html', {'models' : models})


class LoadTemplateView(View):
    template_name = ['app/highcharts.html']

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

'''
class RenderExecutiveView(View):
    template_name = ['app/render_executive.html']

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            scenarios = request.GET.get('scenarios')
            if not scenarios:
                return render(request, self.template_name)
            else:
                return render(request, self.template_name)
'''




'''
def load_ds(request):
    page_id = request.GET.get('ip_page')
    dataset = InputDataSet.objects.filter(input_page_id=page_id).order_by('name')
    return render(request, 'app/ds_dropdown.html', {'dataset': dataset})
'''


# def load_ds(request):
#     ip_page=request.post['Input']
#     print(ip_page)


def search_ds(request):
    if request.method=="POST":
        search_ds = request.POST['data']
        print(search_ds)