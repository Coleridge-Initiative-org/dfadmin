from django.conf.urls import url
from data_facility_admin.api import views

from rest_framework import routers
api_router = routers.SimpleRouter()

api_router.register(r'dfroles', views.DfRoleViewSet)
api_router.register(r'users', views.UserViewSet)
api_router.register(r'datasets', views.DatasetViewSet, basename='dataset')
api_router.register(r'categories', views.CategoryViewSet)
api_router.register(r'projects', views.ProjectViewSet, basename='project')
api_router.register(r'DataStewards'.lower(), views.DataStewardViewSet)
api_router.register(r'DataProviders'.lower(), views.DataProviderViewSet)
api_router.register(r'DatabaseSchema'.lower(), views.DatabaseSchemaViewSet)

urls = [
    url(r'^db-sync', views.DatabaseSyncListView, name='db-sync')
    ]
urls += api_router.urls
