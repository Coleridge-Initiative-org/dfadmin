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
from test_ldap import BaseLdapTestCase


class LdapTestCase(BaseLdapTestCase):

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





