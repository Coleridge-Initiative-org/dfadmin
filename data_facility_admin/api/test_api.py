from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient, RequestsClient

from data_facility_admin import factories, models
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

YESTERDAY = timezone.now() - timezone.timedelta(days=1)
TOMORROW = timezone.now() + timezone.timedelta(days=1)


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
#

#     def test_api_project_list(self):
#         request = self.factory.get(API_BASE + 'projects/', format='json')
#         force_authenticate(request, user=self.user)
#         response = api_views.ProjectViewSet.as_view({'get': 'list'})(request).render()
#         self.assertEqual(status.HTTP_200_OK, response.status_code)
#         self.assertEqual(1, len(response.data['results']))
#         self.assertEqual('test Project', response.data['results'][0]['name'])


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
    # Project

    def test_api_project_do_not_return_data_transfer_projects(self):
        project = factories.ProjectFactory.create(name='My Test Project',
                                                  type=models.Project.PROJECT_TYPE_DATA_TRANSFER,
                                                  status=models.Project.STATUS_ACTIVE,
                                                  start=YESTERDAY)
        user = factories.UserFactory.create()
        project_role = models.ProjectRole.objects.create(name='My Role',
                                                         system_role=models.ProjectRole.SYSTEM_ROLE_ADMIN)
        models.ProjectMember.objects.create(project=project, member=user, role=project_role, start_date=timezone.now())
        response = self.client.get(reverse('project-list', args=[]), format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, response.data['count'])

    def test_api_project_return_class_projects(self):
        project = factories.ProjectFactory.create(name='My Test Project',
                                                  type=models.Project.PROJECT_TYPE_CLASS,
                                                  status=models.Project.STATUS_ACTIVE,
                                                  start=YESTERDAY)
        user = factories.UserFactory.create()
        project_role = models.ProjectRole.objects.create(name='My Role',
                                                         system_role=models.ProjectRole.SYSTEM_ROLE_ADMIN)
        models.ProjectMember.objects.create(project=project, member=user, role=project_role, start_date=timezone.now())
        response = self.client.get(reverse('project-list', args=[]), format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(project.name, response.data['results'][0]['name'])

    def test_api_project_return_research_projects(self):
        project = factories.ProjectFactory.create(name='My Test Project',
                                                  type=models.Project.PROJECT_TYPE_RESEARCH,
                                                  status=models.Project.STATUS_ACTIVE,
                                                  start=YESTERDAY)
        user = factories.UserFactory.create()
        project_role = models.ProjectRole.objects.create(name='My Role',
                                                         system_role=models.ProjectRole.SYSTEM_ROLE_ADMIN)
        models.ProjectMember.objects.create(project=project, member=user, role=project_role, start_date=timezone.now())
        response = self.client.get(reverse('project-list', args=[]), format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(project.name, response.data['results'][0]['name'])

    def test_api_project_return_capstone_projects(self):
        project = factories.ProjectFactory.create(name='My Test Project',
                                                  type=models.Project.PROJECT_TYPE_CAPSTONE,
                                                  status=models.Project.STATUS_ACTIVE,
                                                  start=YESTERDAY)
        user = factories.UserFactory.create()
        project_role = models.ProjectRole.objects.create(name='My Role',
                                                         system_role=models.ProjectRole.SYSTEM_ROLE_ADMIN)
        models.ProjectMember.objects.create(project=project, member=user, role=project_role, start_date=timezone.now())
        response = self.client.get(reverse('project-list', args=[]), format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(project.name, response.data['results'][0]['name'])

    def test_api_projects_dont_return_active_project_without_dates(self):
        project = factories.ProjectFactory.create(name='My Test Project',
                                                  type=models.Project.PROJECT_TYPE_CAPSTONE,
                                                  status=models.Project.STATUS_ACTIVE)
        user = factories.UserFactory.create()
        project_role = models.ProjectRole.objects.create(name='My Role',
                                                         system_role=models.ProjectRole.SYSTEM_ROLE_ADMIN)
        models.ProjectMember.objects.create(project=project, member=user, role=project_role, start_date=timezone.now())
        response = self.client.get(reverse('project-list', args=[]), {'member': user.username}, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, response.data['count'])

    def test_api_projects_return_active_project_with_start_without_end_date(self):
        project = factories.ProjectFactory.create(name='My Test Project',
                                                  type=models.Project.PROJECT_TYPE_CAPSTONE,
                                                  status=models.Project.STATUS_ACTIVE,
                                                  start=YESTERDAY)
        user = factories.UserFactory.create()
        project_role = models.ProjectRole.objects.create(name='My Role',
                                                         system_role=models.ProjectRole.SYSTEM_ROLE_ADMIN)
        models.ProjectMember.objects.create(project=project, member=user, role=project_role, start_date=timezone.now())
        response = self.client.get(reverse('project-list', args=[]), {'member': user.username}, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(project.name, response.data['results'][0]['name'])

    def test_api_projects_return_active_project_with_end_date_future(self):
        project = factories.ProjectFactory.create(name='My Test Project',
                                                  type=models.Project.PROJECT_TYPE_CAPSTONE,
                                                  status=models.Project.STATUS_ACTIVE,
                                                  start=YESTERDAY,
                                                  end=TOMORROW)
        user = factories.UserFactory.create()
        project_role = models.ProjectRole.objects.create(name='My Role',
                                                         system_role=models.ProjectRole.SYSTEM_ROLE_ADMIN)
        models.ProjectMember.objects.create(project=project, member=user, role=project_role, start_date=timezone.now())
        response = self.client.get(reverse('project-list', args=[]), {'member': user.username}, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(project.name, response.data['results'][0]['name'])

    def test_api_projects_dont_return_active_project_with_end_date_past(self):
        project = factories.ProjectFactory.create(name='My Test Project',
                                                  type=models.Project.PROJECT_TYPE_CAPSTONE,
                                                  status=models.Project.STATUS_ACTIVE,
                                                  start=YESTERDAY,
                                                  end=YESTERDAY)
        user = factories.UserFactory.create()
        project_role = models.ProjectRole.objects.create(name='My Role',
                                                         system_role=models.ProjectRole.SYSTEM_ROLE_ADMIN)
        models.ProjectMember.objects.create(project=project, member=user, role=project_role, start_date=timezone.now())
        response = self.client.get(reverse('project-list', args=[]), {'member': user.username}, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, response.data['count'])

    def test_api_project_return_data_transfer_projects_if_data_steward(self):
        project = factories.ProjectFactory.create(name='My Test Data Transfer Project',
                                                  type=models.Project.PROJECT_TYPE_DATA_TRANSFER,
                                                  status=models.Project.STATUS_ACTIVE,
                                                  start=YESTERDAY)
        user = factories.UserFactory.create()
        project_role = models.ProjectRole.objects.create(name='My Role',
                                                         system_role=models.ProjectRole.SYSTEM_ROLE_ADMIN)
        models.ProjectMember.objects.create(project=project, member=user, role=project_role, start_date=timezone.now())
        # Add Curator role
        adrf_curators = models.DfRole.objects.create(name= models.DfRole.ADRF_CURATORS)
        models.UserDfRole.objects.create(user=user, role=adrf_curators, begin=YESTERDAY)
        #Check
        response = self.client.get(reverse('project-list', args=[]), {'member': user.username}, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(project.name, response.data['results'][0]['name'])


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


class JwtAuth(TestCase):

    def setUp(self):
        User.objects.create_superuser(username='daniel', password='secret', email='', is_staff=True)

    @tag('integration')
    def test_check_if_can_read_token(self):
        ACCESS_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ1M0JmcDhSOTVJb0M0Q1pvenpuT2pQZjU5aF9kTm1mX3o4cVlkTkJvSjQ0In0.eyJqdGkiOiJjYTQ1YWZiYi05YWE5LTQzMDktYWRkNC0xNmYxZWZjOGM1MDYiLCJleHAiOjE1NTkyMzMzNzksIm5iZiI6MCwiaWF0IjoxNTU5MjMzMDc5LCJpc3MiOiJodHRwczovL2lkLmFkcmYuaW5mby9hdXRoL3JlYWxtcy9BRFJGIiwiYXVkIjpbImRmYWRtaW4iLCJhY2NvdW50Il0sInN1YiI6IjQ1ZDc3ZWRhLWMwZTItNDVmMS1iZmMyLWNmN2YyM2MwMWE1NyIsInR5cCI6IkJlYXJlciIsImF6cCI6ImRmYWRtaW4iLCJhdXRoX3RpbWUiOjAsInNlc3Npb25fc3RhdGUiOiJlOWRjYjc2My05ZWE4LTRmMWMtODE4ZS0yNDExYzU3YjI2YmUiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHBzOi8vZGZhZG1pbi5hZHJmLmluZm8iXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6InByb2ZpbGUgZW1haWwgRGZBZG1pbl9TY29wZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IkRhbmllbCBDYXN0ZWxsYW5pIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiZGFuaWVsIiwiZ2l2ZW5fbmFtZSI6IkRhbmllbCIsImZhbWlseV9uYW1lIjoiQ2FzdGVsbGFuaSIsImVtYWlsIjoiZGFuaWVsLmNhc3RlbGxhbmlAbnl1LmVkdSJ9.UgjoHvYv7f1Qm7rSvD4XvN5bfp4XsyHejErlnlWra-naNssiOtqVH6W-lThaz7KHG2YgorazIlrh0pq1WhKyqi1vA-bR5OanQ4MWrpxcmR7Crx_GneDTAuN29W3fCivaORxPvFMpc-Wgj05wR-RNjZS8Rh_Db_pkuRlGAD-27fWanYLoVU_W25esM2Yj-Uee8Y9fMlXkmJyvbMOffvlqgcUjBwtrm5vavk3MzsE0QG7Kb0ezq89vx9Z50gCbN5qmj9C3ZGY4XptTMIJmLkF7QcXLqyJuFt3fkpHNY4AihJMmFKhEU9HQZlQQ0DqsMlnuowbcZoaAP-FXAfQBb3YJ1g'

        url = "http://localhost:8000/api/v1/projects"

        querystring = {"member": "rafael", "fields": "name,tools"}

        headers = {
            'Authorization': "Bearer %s" % ACCESS_TOKEN,
            'User-Agent': "PostmanRuntime/7.13.0",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Postman-Token': "001eb74c-572b-495c-9e29-08c24026bc82,2adecb17-0c3a-4d13-89bc-2a32df717cc7",
            'accept-encoding': "gzip, deflate",
            'referer': "https://dfadmin.adrf.info/api/v1/projects?member=rafael&fields=name,tools",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        # print('<response>\n%s \n</response>' % response.text)

        self.assertTrue('Could not deserialize key data' not in response.text)

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
