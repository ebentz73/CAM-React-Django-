from django.urls import path, include
from django.views.generic import TemplateView
from app import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='app/index.html'), name='index'),
    path('eval-job/', include(views.EvalJobViewSet().urls)),
]
