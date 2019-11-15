from django.shortcuts import render
from rest_framework_mongoengine.viewsets import ModelViewSet

from app.models import EvalJob, BaselineConfig, Scenario
from app.serializers import EvalJobSerializer, BaselineConfigSerializer, ScenarioSerializer
from app.utils import run_playbook


def index(request):
    return render(request, 'app/index.html')


def start(request):
    # eval_job = EvalJob.objects.create(name='Eval Job Name',
    #                                   model_url='www.evaljob.com',
    #                                   layers=['2010', '2011', '2012'],
    #                                   nodes=['This is a node', 'This is also node', 'This is not a node', 'Jk, the last one was a node'])
    # print(eval_job.pk)
    run_playbook(tags='gcp', playbook='create-instance.yaml')
    return render(request, 'index.html')


def stop(request):
    run_playbook(tags='gcp', playbook='delete-instance.yaml')
    return render(request, 'index.html')


# Api Views
class EvalJobViewSet(ModelViewSet):
    serializer_class = EvalJobSerializer

    def get_queryset(self):
        return EvalJob.objects.all()


class BaselineConfigViewSet(ModelViewSet):
    serializer_class = BaselineConfigSerializer

    def get_queryset(self):
        return BaselineConfig.objects.all()


class ScenarioViewSet(ModelViewSet):
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        return Scenario.objects.all()
