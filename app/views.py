import docker
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import ExecutiveView
from app.utils import run_playbook
from app.serializers import NodeResultSerializer


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
