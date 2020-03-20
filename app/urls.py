from django.urls import path
from django.conf.urls import url
from app import views

app_name = 'app'
urlpatterns = [
    # path('', views.index, name='index'),
    # url(r'^chart/$', LoadTemplateView.as_view(), name="load_template"),
    path('load_chart/<int:evaljob_id>/', views.load_chart, name="load_chart"),
    path('start/<int:solution_id>/', views.start, name='start'),
    path('stop/', views.stop, name='stop'),
    path('render_executive/<int:executiveview_id>/', views.render_executive, name="render_executive"),
    url(r'^view/', views.search_ds, name='search_ds'),
    path('load-data-set/', views.load_ds, name='ajax_load_data_set'),
    url(r'update/(?P<pk>[0-9]+)/', views.update, name="update"),
    url(r'create_json/(?P<pk>[0-9]+)/', views.create_json, name="create_json"),
]
