from django.shortcuts import render

from app.models import ExecutiveView
from app.utils import run_playbook


def index(request):
    ex = ExecutiveView.objects.get(pk=1)
    return render(request, 'app/index.html', {'exec_view': ex})


def start(request):
    run_playbook(tags='gcp', extra_vars={'run_id': 1}, playbook='create-instance.yaml')
    return render(request, 'index.html')


def stop(request):
    run_playbook(tags='gcp', extra_vars={'run_id': 1}, playbook='delete-instance.yaml')
    return render(request, 'index.html')
