from django.urls import path, include
from django.views.generic import TemplateView
from app import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='app/index.html'), name='index'),
    path('render_executive/<int:executiveview_id>/', views.render_executive, name='render_executive'),
    path('executive-view/', include(views.ExecutiveViewViewSet().urls)),
    path('evaljob/', include(views.EvalJobViewSet().urls)),

    path('load_chart/<int:evaljob_id>/', views.load_chart, name='load_chart'),
    path('stop/', views.stop, name='stop'),
    path('view/', views.search_ds, name='search_ds'),
    path('load-data-set/', views.load_ds, name='ajax_load_data_set'),
]
