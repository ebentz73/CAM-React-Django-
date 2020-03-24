from django.urls import path
from app import views

app_name = 'app'
urlpatterns = [
    path('load_chart/<int:evaljob_id>/', views.load_chart, name="load_chart"),
    path('stop/', views.stop, name='stop'),
    path('render_executive/<int:executiveview_id>/', views.render_executive, name="render_executive"),
    path('view/', views.search_ds, name='search_ds'),
    path('load-data-set/', views.load_ds, name='ajax_load_data_set'),
    path('update/<int:exec_view_id>/', views.update, name='update'),
    path('create_json/<int:pk>/', views.create_json, name='create_json'),
]
