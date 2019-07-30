''' DFAdmin django tests '''
from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User, UserManager
from django.db import IntegrityError
from django.test import Client, TestCase
# from django.test import SimpleTestCase
from parameterized import parameterized

from .models import DfRole
from data_facility_admin import models

# pylint: disable:too-few-public-methods


class MockRequest(object):
    pass

# pylint: disable:too-few-public-methods
class MockSuperUser(object):
    def has_perm(self, perm):
        return True


# TODO: Add test for logic - ldap_name is generated based on name for projects, users and roles.


ADMIN_USERNAME = 'ADMIN'
ADMIN_PASSWD = 'PASSWD'

request = MockRequest()
request.user = MockSuperUser()

# pylint: disable=too-many-public-methods
class AdminSiteTests(TestCase):
    ''' Basic List and Add admin tests.'''

    @classmethod
    def setUpClass(cls):
        super(AdminSiteTests, cls).setUpClass()
        # TODO: Move this admin creation to Test Fixtures
        User.objects.create_superuser(username=ADMIN_USERNAME, password=ADMIN_PASSWD, email='')

    def setUp(self):
        self.admin_user = User.objects.get(username=ADMIN_USERNAME)
        self.clnt = Client()
        self.clnt.login(username=ADMIN_USERNAME, password=ADMIN_PASSWD)
        self.site = AdminSite()

    def test_login_admin_user(self):
        login_result = Client().login(username=ADMIN_USERNAME, password=ADMIN_PASSWD)
        self.assertTrue(login_result, 'Login failed.')

    def test_login(self):
        response = Client().post('/login/', {'name': 'dfadmin', 'passwd': 'dfadmin'})
        self.assertEqual(200, response.status_code)

    def test_df_role_model_admin_has_fields(self):
        ma = ModelAdmin(DfRole, self.site)
        self.assertEqual(set(ma.get_form(request).base_fields),
                         {'ldap_name', 'name', 'description'})

    ERROR_MESSAGE = 'Error accessing {0} page for model: {1}.'
    MODELS = [
        ('User', '/data_facility_admin/',),
        ('DFRole', '/data_facility_admin/',),
        ('TermsOfUse', '/data_facility_admin/',),
        ('Training', '/data_facility_admin/',),
        ('ProfileTag', '/data_facility_admin/',),
        ('Project', '/data_facility_admin/',),
        ('ProjectRole', '/data_facility_admin/',),
        ('ProjectTool', '/data_facility_admin/',),
        ('Category', '/data_facility_admin/',),
        ('Dataset', '/data_facility_admin/',),
        ('DataProvider', '/data_facility_admin/',),
        ('DataSteward', '/data_facility_admin/',),
        ('DatabaseSchema', '/data_facility_admin/',),
        ('DataAgreement', '/data_facility_admin/',),
        ('DataAgreementSignature', '/data_facility_admin/',),
        ('DatasetAccess', '/data_facility_admin/',),
        ('Keyword', '/data_facility_admin/',),
        ('DataClassification', '/data_facility_admin/',),
    ]

    @parameterized.expand(MODELS)
    def test_admin_page_list_model(self, model_name, model_path):
        try:
            self.assertEqual(200, self.clnt.get(model_path + model_name.lower() + '/').status_code,
                             AdminSiteTests.ERROR_MESSAGE.format('list', model_name))
        except Exception as ex:
            print(AdminSiteTests.ERROR_MESSAGE.format('list', model_name))
            raise ex

    @parameterized.expand(MODELS)
    def test_admin_page_search_model(self, model_name, model_path):
        try:
            self.assertEqual(200, self.clnt.get(model_path + model_name.lower() + '/?q=a').status_code,
                             AdminSiteTests.ERROR_MESSAGE.format('search', model_name))
        except Exception as ex:
            print(AdminSiteTests.ERROR_MESSAGE.format('search', model_name))
            raise ex

    @parameterized.expand(MODELS)
    def test_admin_page_add_model(self, model_name, model_path):
        try:
            self.assertEqual(200, self.clnt.get(model_path + model_name.lower() + '/add/').status_code,
                             AdminSiteTests.ERROR_MESSAGE.format('add', model_name))
        except Exception as ex:
            print(AdminSiteTests.ERROR_MESSAGE.format('add', model_name))
            raise ex

    def test_prometheus_metrics(self):
        self.assertEqual(200, Client().get('/prometheus/metrics').status_code)