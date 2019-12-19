from django.urls import path

from app import views

app_name = 'app'
urlpatterns = [
    path('start/', views.start, name='start'),
    path('stop/', views.stop, name='stop'),
    path('', views.index, name='index'),
]
