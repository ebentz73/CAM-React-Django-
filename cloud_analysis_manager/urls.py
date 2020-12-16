"""cloud_analysis_manager URL Configuration

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
from django.urls import path, include
from django.conf.urls import url
from django.views.generic import RedirectView
from material.frontend import urls as frontend_urls
from rest_framework_nested import routers

from app import views

router = routers.SimpleRouter()
router.register(r'api/v1/solutions', views.AnalyticsSolutionViewSet, basename='solutions')

solution_router = routers.NestedSimpleRouter(router, r'api/v1/solutions', lookup='solution')

solution_router.register(r'scenarios', views.ScenarioViewSet, basename='scenarios')
solution_router.register(r'filtercategories', views.FilterCategoryViewSet, basename='filtercategories')
solution_router.register(r'evaljobs',
                         views.EvalJobDefinitionViewSet,
                         basename='evaljobs')
solution_router.register(r'models', views.AnalyticsModelViewSet, basename='models')
solution_router.register(r'nodes', views.NodeViewSet, basename='solution-nodes')
solution_router.register(r'modelnodedatas', views.NodeDataViewSet, basename='solution-modelnodedatas')

model_router = routers.NestedSimpleRouter(solution_router, r'models', lookup='model')
model_router.register(r'nodes', views.NodeViewSet, basename='nodes')

node_router = routers.NestedSimpleRouter(model_router, r'nodes', lookup='node')
node_router.register(r'inputnodedatas', views.InputNodeDataViewSet, basename='node-inputnodedatas')
node_router.register(r'constnodedatas', views.ConstNodeDataViewSet, basename='node-constnodedatas')

scenario_router = routers.NestedSimpleRouter(solution_router, r'scenarios', lookup='scenario')
scenario_router.register(r'inputnodedatas', views.InputNodeDataViewSet, basename='scenario-inputnodedatas')
scenario_router.register(r'constnodedatas', views.ConstNodeDataViewSet, basename='scenario-constnodedatas')
scenario_router.register(r'nodedatas', views.NodeDataViewSet, basename='scenario-nodedatas')

category_router = routers.NestedSimpleRouter(solution_router, r'filtercategories', lookup='filtercategory')
category_router.register(r'filteroptions', views.FilterOptionViewSet, basename='filtercategory-filteroptions')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(solution_router.urls)),
    path('', include(category_router.urls)),
    path('', include(model_router.urls)),
    path('', include(scenario_router.urls)),
    path('', include(node_router.urls)),

    path('microsoft/', include('microsoft_auth.urls', namespace='microsoft')),

    path('', include(frontend_urls)),
    path('', RedirectView.as_view(url='app/')),
    path("admin/", admin.site.urls),
    url("^frontend-app/.*", include("frontend-app.urls")),
    path("app/", include("app.urls")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path(
        "api/evaljob/<int:pk>/",
        views.EvalJobDefinitionViewSet.as_view(
            {"get": "retrieve", "patch": "partial_update"}
        ),
    ),
    path("api/results/", views.NodeResultView.as_view()),

    path("api/model/", views.ModelAPIView.as_view()),

    path('api/solution/<pk>/report/', views.PowerBIAPIView.as_view()),
    path('api/solution/<pk>/scenario/', views.AnalyticsSolutionScenarios.as_view()),
    path("api/solution/", views.AnalyticsSolutionAPIView.as_view()),
    path('api/solution/<pk>/node/', views.NodeBySolutionListAPIView.as_view()),
    path('api/solution/<pk>/filters/', views.FilterCategoriesAndOptionsBySolutionAPIView.as_view()),
    path('api/solution/<pk>/model-node-data/', views.ModelNodeDataBySolutionAPIView.as_view()),

    path("api/scenario/", views.ScenarioAPIView.as_view()),
    path('api/scenario/<pk>/node-data/', views.AllNodeDataByScenarioAPIView.as_view()),
    path('api/scenario/<pk>/', views.ScenarioByIdAPIView.as_view()),

    path("api/node-data/scenario", views.CreateOrUpdateNodeDataByScenario.as_view()),
    path("api/post-scenario", views.CreateOrUpdateScenario.as_view()),
    path("api/input-node-data/", views.InputNodeDataAPIView.as_view()),
    path("api/const-node-data/", views.ConstNodeDataAPIView.as_view()),
    url('^api/const-node-data/node=(?P<node>.+)/$', views.ConstNodeDataByNodeListAPIView.as_view()),
    url('^api/input-node-data/node=(?P<node>.+)/$', views.InputNodeDataByNodeListAPIView.as_view()),
    url('^api/node/model=(?P<model>.+)/$', views.NodeByModelListAPIView.as_view()),

    path('api/user', views.UserAPIView.as_view()),
]
