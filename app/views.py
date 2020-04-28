from functools import wraps

import material.frontend.views as material
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from app.forms import CreateEvalJobForm
from app.models import ExecutiveView, EvalJob
from app.serializers import EvalJobSerializer, NodeResultSerializer


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


class NodeResultView(APIView):
    """Create or update a node result."""

    @staticmethod
    @validate_api(NodeResultSerializer, many=True)
    def post(request, serializer):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
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
