from django.conf.urls import url
from django.urls import path
from app import views

app_name = 'app'
urlpatterns = [
    path('load_chart/<int:evaljob_id>/', views.load_chart, name="load_chart"),
    path('start/', views.start, name='start'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('render_executive/<int:executiveview_id>/<int:scenario_id>/<int:model_id>/', views.render_executive,
         name="render_executive"),
    url(r'^view/', views.search_ds, name='search_ds'),
    path('load-data-set/', views.load_ds, name='ajax_load_data_set'),
    url(r'update/(?P<pk>[0-9]+)/', views.update, name="update"),
    url(r'create_json/(?P<pk>[0-9]+)/', views.create_json, name="create_json"),
]
