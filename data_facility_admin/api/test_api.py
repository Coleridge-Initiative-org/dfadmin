from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient, RequestsClient
from data_facility_admin.api import views as api_views
from data_facility_admin.models import Project, DfRole
from requests.auth import HTTPBasicAuth

ADMIN_USERNAME = 'ADMIN'
ADMIN_PASSWORD = 'PASSWD'
#
PROJECT_NAME = 'test Project'
PROJECT_LDAP_NAME = 'project-test-project'
PROJECT_ABSTRACT = 'abstract'
#
DF_ROLE_NAME = 'test name'
DF_ROLE_DESCRIPTION = 'test description'
#
SERVER_URL = 'http://localhost:8000'
API_BASE = '/api/v1/'


class ApiTests(TestCase):

    @classmethod
    def setUpClass(cls):
        # TODO: Move this admin creation to Test Fixtures
        super(ApiTests, cls).setUpClass()
        User.objects.create_superuser(username=ADMIN_USERNAME, password=ADMIN_PASSWORD, email='')
        #
        test_project = Project(name=PROJECT_NAME,
                               ldap_name=PROJECT_LDAP_NAME,
                               abstract=PROJECT_ABSTRACT)
        test_project.save()

        test_dfrole = DfRole(name=DF_ROLE_NAME,
                               description=DF_ROLE_DESCRIPTION)
        test_dfrole.save()

    def setUp(self):
        self.settings(DEBUG=False)
        self.factory = APIRequestFactory()
        self.user = User.objects.get(username=ADMIN_USERNAME)

    # Authentication
    def test_api_needs_authentication(self):
        request = self.factory.get(API_BASE, format='json')
        response = api_views.DatabaseSyncListView(request)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_api_works_with_authentication(self):
        request = self.factory.get(API_BASE, format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatabaseSyncListView(request)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

# DB-Sync API
    def test_api_db_sync(self):
        request = self.factory.get(API_BASE + 'db-sync', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatabaseSyncListView(request)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_api_db_sync_has_all_projects(self):
        request = self.factory.get(API_BASE + 'db-sync', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatabaseSyncListView(request)
        self.assertEqual(Project.objects.count(), len(response.data['results']))

    def test_api_db_sync_has_the_test_project(self):
        request = self.factory.get(API_BASE + 'db-sync', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatabaseSyncListView(request)
        project_names = [project['name'] for project in response.data['results']]
        assert PROJECT_NAME in project_names

    def test_api_db_sync_has_active_member_permissions(self):
        request = self.factory.get(API_BASE + 'db-sync', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatabaseSyncListView(request)
        assert response.data
        project_data = response.data['results'][0]
        assert 'active_member_permissions' in project_data

    def test_api_db_sync_has_db_schema(self):
        request = self.factory.get(API_BASE + 'db-sync', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatabaseSyncListView(request)
        assert response.data
        project_data = response.data['results'][0]
        assert 'db_schema' in project_data

    def test_api_db_sync_has_datasets_with_access(self):
        request = self.factory.get(API_BASE + 'db-sync', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatabaseSyncListView(request)
        project_data = response.data['results'][0]
        assert 'datasets_with_access' in project_data

    def test_api_db_sync_has_ldap_name(self):
        request = self.factory.get(API_BASE + 'db-sync', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatabaseSyncListView(request)
        project_data = response.data['results'][0]
        assert 'ldap_name' in project_data

    def test_api_db_sync_has_status(self):
        request = self.factory.get(API_BASE + 'db-sync', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatabaseSyncListView(request)
        project_data = response.data['results'][0]
        assert 'status' in project_data

    def test_api_db_sync_has_environment(self):
        request = self.factory.get(API_BASE + 'db-sync', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatabaseSyncListView(request)
        project_data = response.data['results'][0]
        assert 'environment' in project_data

# DfRole API
    def test_api_dfrole_list(self):
        request = self.factory.get(API_BASE + 'dfroles/', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DfRoleViewSet.as_view({'get': 'list'})(request).render()
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_api_dfrole_detail(self):
        request = self.factory.get(API_BASE + 'dfroles/1/', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DfRoleViewSet.as_view({'get': 'list'})(request, pk=1).render()
        self.assertEqual(status.HTTP_200_OK, response.status_code)

# Dataset
    def test_api_dataset_list(self):
        request = self.factory.get(API_BASE + 'datasets/', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DfRoleViewSet.as_view({'get': 'list'})(request).render()
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_api_dfrole_detail(self):
        request = self.factory.get(API_BASE + 'datasets/1/', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DfRoleViewSet.as_view({'get': 'list'})(request, pk=1).render()
        self.assertEqual(status.HTTP_200_OK, response.status_code)

# Project
    def test_api_project_list(self):
        request = self.factory.get(API_BASE + 'projects/', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DfRoleViewSet.as_view({'get': 'list'})(request).render()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data['results']))
        self.assertEqual('test name', response.data['results'][0]['name'])


class ApiClientTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ApiClientTests, cls).setUpClass()
        # TODO: Move this admin creation to Test Fixtures
        User.objects.create_superuser(username=ADMIN_USERNAME, password=ADMIN_PASSWORD, email='')
        test_dfrole = DfRole(name=DF_ROLE_NAME,
                             description=DF_ROLE_DESCRIPTION)
        test_dfrole.save()

    def setUp(self):
        self.client = APIClient()
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)

    def test_api_client_dfrole_list(self):
        response = self.client.get(reverse('dfrole-list', args=[]), format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_api_project_list(self):
        response = self.client.get(reverse('project-list', args=[]), format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

#
# class RequestClientTests(TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         super(RequestClientTests, cls).setUpClass()
#         # TODO: Move this admin creation to Test Fixtures
#         User.objects.create_superuser(username=ADMIN_USERNAME, password=ADMIN_PASSWORD, email='')
#         test_dfrole = DfRole(name=DF_ROLE_NAME,
#                              description=DF_ROLE_DESCRIPTION)
#         test_dfrole.save()
#
#     def setUp(self):
#         self.client = RequestsClient()
#         self.client.auth = HTTPBasicAuth(ADMIN_USERNAME, ADMIN_PASSWORD)
#
#     def test_api_client_dfrole_list(self):
#         response = self.client.get('http://localhost/api/dfroles/')
#         print response.content
#         self.assertEqual(status.HTTP_200_OK, response.status_code)
#
#     def test_api_client_dfrole_list_format_json(self):
#         response = self.client.get('http://localhost/api/dfroles/?format=json')
#         self.assertEqual(status.HTTP_200_OK, response.status_code)
