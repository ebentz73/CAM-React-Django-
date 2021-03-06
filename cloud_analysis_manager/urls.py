"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from app.views import EvalJobViewSet, BaselineConfigViewSet, ScenarioViewSet

# We use a single global DRF Router that routes views from all apps in project
router = routers.DefaultRouter()

# app views and viewsets
router.register('eval', EvalJobViewSet, 'eval')
router.register('baseline', BaselineConfigViewSet, 'baseline')
router.register('scenario', ScenarioViewSet, 'scenario')

urlpatterns = [
    # default django admin interface (currently unused)
    path('admin/', admin.site.urls),
    re_path(r'^$', TemplateView.as_view(template_name='index.html')),

    # root view of our REST app
    re_path(r'^api/v1/', include(router.urls)),

    path('app/', include('app.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
