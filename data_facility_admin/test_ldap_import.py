from django.test import TestCase
from data_facility_admin.models import *
from data_facility_admin.helpers import LDAPHelper 
import mock
from mockldap import MockLdap
from django.conf import settings
import ldap
from django.utils import timezone
import datetime
import pytz

class LdapTestCase(TestCase):
    USER_LDAP_ID = LdapObject.MIN_LDAP_UID
    USER_FULL_DN = 'uid=johnlennon,ou=people,dc=adrf,dc=info'
    USER_GROUP_FULL_DN = 'cn=johnlennon,ou=groups,dc=adrf,dc=info' 

    def setUp(self):
        info = ('dc=info', { 'dc': ['info']})
        adrf = ('dc=adrf,dc=info', { 'dc': ['adrf']})
        admin = ('cn=admin,dc=adrf,dc=info', { 'cn': [ 'admin'], 'userPassword': [ '???']})
        people = ('ou=People,dc=adrf,dc=info', { 'ou': ['People']})
        groups = ('ou=Groups,dc=adrf,dc=info', { 'ou': ['Groups']})
        projects = ('ou=Projects,dc=adrf,dc=info', { 'ou': ['Projects']})
        datasets = ('ou=Datasets,dc=adrf,dc=info', { 'ou': ['Datasets']})

        directory = dict([info, adrf, admin, people, groups, projects, datasets])
        self.mockldap = MockLdap(directory)
        self.mockldap.start()
        self.ldapobj = self.mockldap['ldaps://meat.adrf.info']

    def tearDown(self):
        self.mockldap.stop()
        del self.ldapobj

    def setUser(self, ldap_id=USER_LDAP_ID, ldap_name=None, first_name="John",
            last_name="Lennon",
            email="johnlennon@adrf.info.dev",
            status=User.STATUS_ACTIVE,
            ldap_last_auth_time=None,
            ldap_lock_time=None,
            ldap_last_pwd_change=None,
            created_at=None,
            updated_at=None,
            system_user=False):
        result = User.objects.filter(ldap_id=ldap_id)
        if len(result) == 0:
            u = User(ldap_id=ldap_id)
        else:
            u = result[0]
        u.first_name = first_name
        u.last_name = last_name
        u.email = email
        u.status = status
        u.system_user = system_user
        if ldap_last_auth_time:
            u.ldap_last_auth_time = ldap_last_auth_time
        if ldap_lock_time:
            u.ldap_lock_time = ldap_lock_time
        if ldap_last_pwd_change:
            u.ldap_last_pwd_change = ldap_last_pwd_change
        if ldap_name:
            u.ldap_name = ldap_name
        if created_at:
            u.created_at = created_at
        u.save()


    @mock.patch('data_facility_admin.helpers.KeycloakHelper')
    def test_ldap_import_auth_time(self, mock_keycloak):
        self.setUser(status=User.STATUS_NEW)
        self.assertTrue(len(User.objects.all()) == 1, "The database should have only one user")

        ldap_helper = LDAPHelper()

        ldap_helper.export_users()

        self.assertTrue(self.USER_FULL_DN in self.ldapobj.directory, "The user should have been inserted")
        self.assertTrue(self.USER_GROUP_FULL_DN in self.ldapobj.directory, "The user private group should have been inserted")

        auth_time = timezone.now()
        auth_time = auth_time.replace(microsecond=0)
        auth_time_utc = auth_time.replace(tzinfo=pytz.utc)
        self.ldapobj.directory[self.USER_FULL_DN][settings.USER_LDAP_MAP["ldap_last_auth_time"]] = [ auth_time_utc.strftime("%Y%m%d%H%M%SZ") ]

        ldap_helper.import_users()

        user = User.objects.filter(ldap_id=self.USER_LDAP_ID)[0]

        self.assertEqual(user.ldap_last_auth_time, auth_time)


    @mock.patch('data_facility_admin.helpers.KeycloakHelper')
    def test_ldap_import_last_pwd_change(self, mock_keycloak):
        self.setUser(status=User.STATUS_NEW)
        self.assertTrue(len(User.objects.all()) == 1, "The database should have only one user")

        ldap_helper = LDAPHelper()

        ldap_helper.export_users()

        self.assertTrue(self.USER_FULL_DN in self.ldapobj.directory, "The user should have been inserted")
        self.assertTrue(self.USER_GROUP_FULL_DN in self.ldapobj.directory, "The user private group should have been inserted")

        last_pwd_change = timezone.now()
        last_pwd_change = last_pwd_change.replace(microsecond=0)
        last_pwd_change_utc = last_pwd_change.replace(tzinfo=pytz.utc)
        self.ldapobj.directory[self.USER_FULL_DN][settings.USER_LDAP_MAP["ldap_last_pwd_change"]] = [ last_pwd_change_utc.strftime("%Y%m%d%H%M%SZ") ]

        ldap_helper.import_users()

        user = User.objects.filter(ldap_id=self.USER_LDAP_ID)[0]

        self.assertEqual(user.ldap_last_pwd_change, last_pwd_change)

    @mock.patch('data_facility_admin.helpers.KeycloakHelper')
    def test_ldap_import_lock_time(self, mock_keycloak):
        self.setUser(status=User.STATUS_NEW)
        self.assertTrue(len(User.objects.all()) == 1, "The database should have only one user")

        ldap_helper = LDAPHelper()

        ldap_helper.export_users()

        self.assertTrue(self.USER_FULL_DN in self.ldapobj.directory, "The user should have been inserted")
        self.assertTrue(self.USER_GROUP_FULL_DN in self.ldapobj.directory, "The user private group should have been inserted")

        self.ldapobj.directory[self.USER_FULL_DN][settings.USER_LDAP_MAP["ldap_last_auth_time"]] = ["000001010000Z"]

        ldap_helper.import_users()

        user = User.objects.filter(ldap_id=self.USER_LDAP_ID)[0]

        self.assertIsNone(user.ldap_lock_time)

        ldap_lock_time = timezone.now()
        ldap_lock_time = ldap_lock_time.replace(microsecond=0)
        ldap_lock_time_utc = ldap_lock_time.replace(tzinfo=pytz.utc)
        self.ldapobj.directory[self.USER_FULL_DN][settings.USER_LDAP_MAP["ldap_lock_time"]] = [ ldap_lock_time_utc.strftime("%Y%m%d%H%M%SZ") ]

        ldap_helper.import_users()

        user = User.objects.filter(ldap_id=self.USER_LDAP_ID)[0]

        self.assertEqual(user.ldap_lock_time, ldap_lock_time)
        self.assertEqual(user.status, User.STATUS_LOCKED_WRONG_PASSWD)

        ldap_lock_time_utc = ldap_lock_time_utc - datetime.timedelta(seconds=settings.LDAP_SETTINGS['General']['PpolicyLockDownDurationSeconds'] + 100) 
        self.ldapobj.directory[self.USER_FULL_DN][settings.USER_LDAP_MAP["ldap_lock_time"]] = [ ldap_lock_time_utc.strftime("%Y%m%d%H%M%SZ") ]

        ldap_helper.import_users()

        user = User.objects.filter(ldap_id=self.USER_LDAP_ID)[0]

        self.assertIsNone(user.ldap_lock_time, "The import script should remove pwdAccountLockedTime from LDAP when activating the user.")
        self.assertEqual(user.status, User.STATUS_ACTIVE)





