from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient, RequestsClient
from data_facility_admin.api import views as api_views
from data_facility_admin.models import Project, DfRole
import requests
from requests.auth import HTTPBasicAuth
from django.test import tag
from parameterized import parameterized


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
        test_project = Project(name=PROJECT_NAME, ldap_name=PROJECT_LDAP_NAME, abstract=PROJECT_ABSTRACT)
        test_project.save()
        #
        test_dfrole = DfRole(name=DF_ROLE_NAME, description=DF_ROLE_DESCRIPTION)
        test_dfrole.save()

    def setUp(self):
        self.settings(DEBUG=False)
        self.factory = APIRequestFactory()
        self.user = User.objects.get(username=ADMIN_USERNAME)

    # Authentication
    def test_api_needs_authentication(self):
        request = self.factory.get(API_BASE, format='json')
        response = api_views.DatabaseSyncListView(request)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

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
        response = api_views.DatasetViewSet.as_view({'get': 'list'})(request).render()
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_api_dataset_list_param_omit_detailed_metadata(self):
        request = self.factory.get(API_BASE + 'datasets/?omit=detailed_metadata', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatasetViewSet.as_view({'get': 'list'})(request).render()
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_api_dataset_list_param_access_type(self):
        request = self.factory.get(API_BASE + 'datasets/?access_type=private', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatasetViewSet.as_view({'get': 'list'})(request).render()
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_api_dataset_list_param_data_provider_name(self):
        request = self.factory.get(API_BASE + 'datasets/?data_provider__name=a', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatasetViewSet.as_view({'get': 'list'})(request).render()
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_api_dataset_list_param_category(self):
        request = self.factory.get(API_BASE + 'datasets/?category__name=a', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatasetViewSet.as_view({'get': 'list'})(request).render()
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_api_dataset_list_param_limit(self):
        request = self.factory.get(API_BASE + 'datasets/?limit=1', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatasetViewSet.as_view({'get': 'list'})(request).render()
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_api_dataset_list_param_offset(self):
        request = self.factory.get(API_BASE + 'datasets/?offset=1', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatasetViewSet.as_view({'get': 'list'})(request).render()
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_api_dataset_detail_param_fields_metadata(self):
        request = self.factory.get(API_BASE + 'datasets/1/?fields=detailed_metadata', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.DatasetViewSet.as_view({'get': 'list'})(request, pk=1).render()
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    # def test_api_dataset_has_search_metadata(self):
    #     request = self.factory.get(API_BASE + 'datasets/', format='json')
    #     force_authenticate(request, user=self.user)
    #     response = api_views.DatasetViewSet.as_view({'get': 'list'})(request).render()
    #     data = response.data['results']
    #     print('data=', data)
    #     assert 'search_metadata' in data

# Project
    def test_api_project_list(self):
        request = self.factory.get(API_BASE + 'projects/', format='json')
        force_authenticate(request, user=self.user)
        response = api_views.ProjectViewSet.as_view({'get': 'list'})(request).render()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data['results']))
        self.assertEqual('test Project', response.data['results'][0]['name'])


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

    # def test_api_client_dfrole_list(self):
    #     response = self.client.get(reverse('dfrole-list', args=[]), format='json')
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)
    #
    # def test_api_project_list(self):
    #     response = self.client.get(reverse('project-list', args=[]), format='json')
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)

    # Some APIs for models were not created yet, so they're commented.
    MODELS = [
        ('User', '/data_facility_admin/',),
        ('DFRole', '/data_facility_admin/',),
        ('Category', '/data_facility_admin/',),
        # ('TermsOfUse', '/data_facility_admin/',),
        # ('Training', '/data_facility_admin/',),
        # ('ProfileTag', '/data_facility_admin/',),
        ('Project', '/data_facility_admin/',),
        # ('ProjectRole', '/data_facility_admin/',),
        # ('ProjectTool', '/data_facility_admin/',),
        ('Dataset', '/data_facility_admin/',),
        ('DataProvider', '/data_facility_admin/',),
        ('DataSteward', '/data_facility_admin/',),
        # ('DatabaseSchema', '/data_facility_admin/',),
        # ('DataAgreement', '/data_facility_admin/',),
        # ('DataAgreementSignature', '/data_facility_admin/',),
        # ('DatasetAccess', '/data_facility_admin/',),
        # ('Keyword', '/data_facility_admin/',),
        # ('DataClassification', '/data_facility_admin/',),
    ]

    @parameterized.expand(MODELS)
    def test_api_list_model(self, model_name, model_path):
        response = self.client.get(reverse(model_name.lower() + '-list', args=[]), format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    @parameterized.expand(MODELS)
    def test_api_list_search_model(self, model_name, model_path):
        response = self.client.get(reverse(model_name.lower() + '-list', args=[]), search='a', format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    # @parameterized.expand(MODELS)
    # def test_api_detail_model(self, model_name, model_path):
    #     response = self.client.get(reverse(model_name.lower() + '-detail', args=[]), format='json')
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)


class ApiAuthorizationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ApiAuthorizationTests, cls).setUpClass()
        # TODO: Move this admin creation to Test Fixtures
        User.objects.create_superuser(username=ADMIN_USERNAME, password=ADMIN_PASSWORD, email='')
        test_dfrole = DfRole(name=DF_ROLE_NAME, description=DF_ROLE_DESCRIPTION)
        test_dfrole.save()

    # Token Authentication
    def test_token_authentication(self):
        # Create token
        admin = User.objects.get(username=ADMIN_USERNAME)
        token = Token.objects.create(user=admin)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.get(SERVER_URL + API_BASE + 'users/?ldap_name=tdiogo')
        self.assertEqual(status.HTTP_200_OK, response.status_code,
                         "Status is not 200, but %s. Reponse: %s" % (response.status_code, response.content))

    def test_token_authentication_does_not_work_with_fake_token(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token abcd')
        response = client.get(SERVER_URL + API_BASE + 'users/?ldap_name=tdiogo')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code,
                         "Status is not 401. Reponse: %s" % response.content)


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
