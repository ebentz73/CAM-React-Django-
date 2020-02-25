from django.urls import path
from django.conf.urls import url
#Here you import from views the view you created
from .views import LoadTemplateView
from app import views


app_name = 'app'
urlpatterns = [
    path('start/', views.start, name='start'),
    path('stop/', views.stop, name='stop'),
    #path('', views.index, name='index'),
    url(r'^chart/$', LoadTemplateView.as_view(), name="load_template"),
    path('render_executive/', views.render_executive, name="render_executive"),
    url(r'^view/', views.search_ds, name='search_ds'),
    path('load-data-set/', views.load_ds, name='ajax_load_data_set'),
]