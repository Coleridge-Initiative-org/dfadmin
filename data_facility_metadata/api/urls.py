from rest_framework import routers
from data_facility_metadata.api import views


api_router = routers.SimpleRouter()
api_router.register(r'FileFormats'.lower(), views.FileFormatViewSet)
api_router.register(r'Files'.lower(), views.FileViewSet)
api_router.register(r'DataTables'.lower(), views.DataTableViewSet)
api_router.register(r'StorageTypes'.lower(), views.StorageTypeViewSet)
api_router.register(r'DataStores'.lower(), views.DataStoreViewSet)
api_router.register(r'PhysicalDataTables'.lower(), views.PhysicalDataTableViewSet)
api_router.register(r'DataTypes'.lower(), views.DataTypeViewSet)
api_router.register(r'Variables'.lower(), views.VariableViewSet)

urls = api_router.urls