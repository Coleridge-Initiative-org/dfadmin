''' URLS for DFAdmin '''
from django.conf.urls import include, url
from django.contrib import admin
from data_facility_admin.api import urls as admin_router
from data_facility_metadata.api import urls as metadata_router
from rest_framework_swagger.views import get_swagger_view
from ajax_select import urls as ajax_select_urls
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import OpenAPIRenderer

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
    url(r'^', admin.site.urls),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # url('^accounts/', admin.site.urls),

    # django-ajax-select
    url(r'^ajax_select/', include(ajax_select_urls)),
    url(r'^nested_admin/', include('nested_admin.urls')),
]

# API
DFADMIN_API = 'DFAdmin API'

api_urls = admin_router.urls
api_urls += metadata_router.urls

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api/v1/', include(api_urls)),#,  namespace='api')),
    url(r'^api/v1/schema.json$', get_schema_view(title=DFADMIN_API, renderer_classes=[OpenAPIRenderer]), name='api-schema'),
    url(r'^api/v1/docs/swagger/$', get_swagger_view(title=DFADMIN_API), name='api-swagger'),
    url(r'^api/v1/docs/open-api/', include_docs_urls(title=DFADMIN_API), name='api-docs'),
]


# # Admin to work on /
# urlpatterns += [
#     url(r'^', admin.site.urls),
# ]