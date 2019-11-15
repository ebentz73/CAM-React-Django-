from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from app import views

app_name = 'app'
urlpatterns = [
    path('start/', views.start, name='start'),
    path('stop/', views.stop, name='stop'),
    path('', views.index, name='index'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
