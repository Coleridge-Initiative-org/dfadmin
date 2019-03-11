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
        ('DataStore', '/data_facility_metadata/',),
        ('DataType', '/data_facility_metadata/',),
        ('FileFormat', '/data_facility_metadata/',),
        ('File', '/data_facility_metadata/',),
        ('StorageType', '/data_facility_metadata/',),
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
