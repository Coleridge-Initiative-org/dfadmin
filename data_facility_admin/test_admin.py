''' DFAdmin django tests '''
from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User, UserManager
from django.db import IntegrityError
from django.test import Client, TestCase
# from django.test import SimpleTestCase

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

# List Page

    def test_list_data_agreement_signature(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/dataagreementsignature/').status_code)

    def test_list_data_agreements(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/dataagreement/').status_code)

    def test_list_dataset_access(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/datasetaccess/').status_code)

    def test_list_datasets(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/dataset/').status_code)

    def test_list_profile_tags(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/profiletag/').status_code)

    def test_list_research_projects(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/project/').status_code)

    def test_list_roles(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/dfrole/').status_code)

    def test_list_terms_of_use(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/termsofuse/').status_code)

    def test_list_training(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/training/').status_code)

    def test_list_users(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/user/').status_code)

    def test_list_database_schema(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/databaseschema/').status_code)

# List Page - search

    def test_search_users(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/user/?q=a').status_code)

    def test_search_data_agreement_signature(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/dataagreementsignature/?q=a').status_code)

    def test_search_data_agreements(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/dataagreement/?q=a').status_code)

    def test_search_dataset_access(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/datasetaccess/?q=a').status_code)

    def test_search_datasets(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/dataset/?q=a').status_code)

    def test_search_profile_tags(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/profiletag/?q=a').status_code)

    def test_search_research_projects(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/project/?q=a').status_code)

    def test_search_roles(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/dfrole/?q=a').status_code)

    def test_search_terms_of_use(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/termsofuse/?q=a').status_code)

    def test_search_training(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/training/?q=a').status_code)

    def test_search_database_schema(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/databaseschema/?q=a').status_code)

# Add Page

    def test_add_data_agreement_signature(self):
        self.assertEqual(200,
                         self.clnt.get('/data_facility_admin/dataagreementsignature/add/').status_code)

    def test_add_data_agreement(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/dataagreement/add/').status_code)

    def test_add_dataset_access(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/datasetaccess/add/').status_code)

    def test_add_dataset(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/dataset/add/').status_code)

    def test_add_profile_tag(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/profiletag/add/').status_code)

    def test_add_research_project(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/project/add/').status_code)

    def test_add_role(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/dfrole/add/').status_code)

    # TODO: Add test for signed terms of use from user page.

    def test_add_terms_of_use(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/termsofuse/add/').status_code)

    def test_add_training(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/training/add/').status_code)

    def test_add_user(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/user/add/').status_code)

    def test_add_database_schema(self):
        self.assertEqual(200, self.clnt.get('/data_facility_admin/databaseschema/add/').status_code)

    def test_df_role_model_admin_has_fields(self):
        ma = ModelAdmin(DfRole, self.site)
        self.assertEqual(set(ma.get_form(request).base_fields),
                         {'ldap_name', 'name', 'description'})
