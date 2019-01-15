from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from parameterized import parameterized
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient, RequestsClient
from django.contrib.auth.models import User
import factories
import utils
from data_facility_admin.api.urls import urls as api_urls

ADMIN_USERNAME = 'ADMIN'
ADMIN_PASSWORD = 'PASSWD'


class DynamicApiTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super(DynamicApiTests, cls).setUpClass()
        # TODO: Move this admin creation to Test Fixtures
        User.objects.create_superuser(username=ADMIN_USERNAME, password=ADMIN_PASSWORD, email='')
        test_dfrole = factories.DfRoleFactory.create()

    def setUp(self):
        self.client = APIClient()
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)

    MODELS = [('project'),
              ('dfrole'),
              ('dataset'),
              ('user'),
              ]
    # MODELS = lambda: [url.replace('^', '').replace('/$', '')
    #                   for url in utils.show_urls(api_urls) if '(?P<pk>[^/.]+)' not in url]

    @parameterized.expand(MODELS)
    def test_api_list(self, model):
        response = self.client.get(reverse('%s-list' % model, args=[]), format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    # @parameterized.expand(MODELS)
    # def test_api_list(self, model):
    #     response = self.client.get(reverse('%s-detail' % model, args=[1]), format='json')
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)