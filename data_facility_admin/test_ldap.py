from django.test import TestCase
from data_facility_admin.models import *
from data_facility_admin.helpers import LDAPHelper
import mock
from mockldap import MockLdap
from django.conf import settings
import ldap
from django.utils import timezone
import datetime


class BaseLdapTestCase(TestCase):
    USER_LDAP_ID = LdapObject.MIN_LDAP_UID
    USER_FULL_DN = 'uid=johnlennon,ou=people,' + settings.LDAP_BASE_DN
    USER_GROUP_FULL_DN = 'cn=johnlennon,ou=groups,' + settings.LDAP_BASE_DN

    def setUp(self):
        info = ('dc=local', { 'dc': ['local']})
        adrf = (settings.LDAP_BASE_DN, { 'dc': ['dfadmin']})
        admin = (settings.LDAP_SETTINGS['Connection']['BindDN'],
                 { 'cn': [ 'admin'], 'userPassword': [settings.LDAP_SETTINGS['Connection']['BindPassword']]})
        people = ('ou=People,' + settings.LDAP_BASE_DN, {'ou': ['People']})
        groups = ('ou=Groups,' + settings.LDAP_BASE_DN, {'ou': ['Groups']})
        projects = ('ou=Projects,' + settings.LDAP_BASE_DN, {'ou': ['Projects']})
        datasets = ('ou=Datasets,' + settings.LDAP_BASE_DN, {'ou': ['Datasets']})

        directory = dict([info, adrf, admin, people, groups, projects, datasets])
        self.mockldap = MockLdap(directory)
        self.mockldap.start()
        self.ldapobj = self.mockldap[settings.LDAP_SERVER]

    def tearDown(self):
        self.mockldap.stop()
        del self.ldapobj

    @classmethod
    def setUser(cls, ldap_id=USER_LDAP_ID, ldap_name=None, first_name="John",
                last_name="Lennon",
                email="johnlennon@dfadmin.local",
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


class LdapTestCase(BaseLdapTestCase):

    @mock.patch('data_facility_admin.helpers.KeycloakHelper')
    def test_ldap_pending_approval_user(self, mock_keycloak):
        self.setUser(status=User.STATUS_PENDING_APPROVAL)
        self.assertTrue(len(User.objects.all()) == 1, "The databse should have only one user")

        ldap_helper = LDAPHelper()
        values = ldap_helper.flat_attributes_from_settings(settings.USER_LDAP_MAP.values())
        self.ldapobj.search_s.seed(settings.LDAP_USER_SEARCH, ldap.SCOPE_SUBTREE, '(uid=*)', values)([])

        LDAPHelper().export_users()

        self.assertTrue(len([x for x in self.ldapobj.methods_called() if x == 'add_s']) == 0, "The add_s method should inot have been called")
        self.assertFalse(self.USER_FULL_DN in self.ldapobj.directory, "The user should have been inserted")
        self.assertFalse(self.USER_GROUP_FULL_DN in self.ldapobj.directory, "The user private group should have been inserted")
       

    @mock.patch('data_facility_admin.helpers.KeycloakHelper')
    def test_ldap_new_user(self, mock_keycloak):
        self.setUser(status=User.STATUS_NEW)
        self.assertTrue(len(User.objects.all()) == 1, "The databse should have only one user")

        ldap_helper = LDAPHelper()
#        values = ldap_helper.flat_attributes_from_settings(settings.USER_LDAP_MAP.values())
#        self.ldapobj.search_s.seed(settings.LDAP_USER_SEARCH, ldap.SCOPE_SUBTREE, '(uid=*)', values)([])

        LDAPHelper().export_users()


        self.assertTrue(len([x for x in self.ldapobj.methods_called() if x == 'add_s']) == 2, "The add_s method should have been called twice")
        self.assertTrue(self.USER_FULL_DN in self.ldapobj.directory, "The user should have been inserted")
        self.assertTrue(self.USER_GROUP_FULL_DN in self.ldapobj.directory, "The user private group should have been inserted")

    @mock.patch('data_facility_admin.helpers.KeycloakHelper')
    def test_ldap_user_updates(self, mock_keycloak):
        self.setUser(status=User.STATUS_NEW)

        self.assertEqual(len(User.objects.all()), 1, "The databse should have only one user")

        ldap_helper = LDAPHelper()
        ldap_helper.export_users()

        self.assertEqual(self.ldapobj.directory[self.USER_FULL_DN][settings.USER_LDAP_MAP["first_name"]][0], "John", "Ldap Should have the original first_name")


        self.setUser(first_name="Rafael")
        self.assertEqual(len(User.objects.all()), 1, "The databse should have only one user")

        ldap_helper.export_users()
        
        self.assertEqual(self.ldapobj.directory[self.USER_FULL_DN][settings.USER_LDAP_MAP["first_name"]][0], "Rafael", "LDAP should have the new first name")
        self.assertEqual(self.ldapobj.directory[self.USER_FULL_DN]["cn"][0], "Rafael Lennon", "LDAP should have the a new full name")

        self.setUser(first_name="Rafael", last_name="Alves")
        self.assertEqual(len(User.objects.all()), 1, "The databse should have only one user")

        ldap_helper.export_users()
        
        self.assertEqual(self.ldapobj.directory[self.USER_FULL_DN][settings.USER_LDAP_MAP["last_name"]][0], "Alves", "LDAP should have the new last_name")
        self.assertEqual(self.ldapobj.directory[self.USER_FULL_DN]["cn"][0], "Rafael Alves")

        self.setUser(first_name="Rafael", last_name="Alves", email="rafael.alves@adrf.info.dev")
        self.assertEqual(len(User.objects.all()), 1, "The databse should have only one user")

        ldap_helper.export_users()
        
        self.assertEqual(self.ldapobj.directory[self.USER_FULL_DN][settings.USER_LDAP_MAP["email"]][0], "rafael.alves@adrf.info.dev", "Check if the email has been updated in LDAP")



    @mock.patch('data_facility_admin.helpers.KeycloakHelper')
    def test_ldap_locking_and_unlocking_user(self, mock_keycloak):
        self.setUser(status=User.STATUS_NEW)

        ldap_helper = LDAPHelper()
        ldap_helper.export_users()

        self.setUser(status=User.STATUS_LOCKED_BY_ADMIN)
        
        ldap_helper.export_users()

        self.assertIn(settings.USER_LDAP_MAP["ldap_lock_time"], self.ldapobj.directory[self.USER_FULL_DN])
        self.assertEqual(self.ldapobj.directory[self.USER_FULL_DN][settings.USER_LDAP_MAP["ldap_lock_time"]][0], "000001010000Z")
        
        self.setUser(status=User.STATUS_UNLOCKED_BY_ADMIN)

        ldap_helper.export_users()

        self.assertNotIn(settings.USER_LDAP_MAP["ldap_lock_time"], self.ldapobj.directory[self.USER_FULL_DN])

    @mock.patch('data_facility_admin.helpers.KeycloakHelper')
    def test_ldap_disabling_user(self, mock_keycloak):
        self.setUser(status=User.STATUS_NEW)

        ldap_helper = LDAPHelper()
        ldap_helper.export_users()

        self.setUser(status=User.STATUS_DISABLED)
        
        ldap_helper.export_users()

        self.assertIn(settings.USER_LDAP_MAP["ldap_lock_time"], self.ldapobj.directory[self.USER_FULL_DN])
        self.assertEqual(self.ldapobj.directory[self.USER_FULL_DN][settings.USER_LDAP_MAP["ldap_lock_time"]][0], "000001010000Z")
        

    @mock.patch('data_facility_admin.helpers.KeycloakHelper')
    def test_ldap_inactive_users_last_auth_time(self, mock_keycloak):
        self.setUser(status=User.STATUS_NEW)

        ldap_helper = LDAPHelper()
        ldap_helper.export_users()

        self.setUser(ldap_last_auth_time=timezone.now() - datetime.timedelta(60, 0, 0))
        
        ldap_helper.export_users()
        
        self.assertEqual(User.STATUS_LOCKED_INACTIVITY, User.objects.filter(ldap_id=self.USER_LDAP_ID)[0].status)

        self.assertIn(settings.USER_LDAP_MAP["ldap_lock_time"], self.ldapobj.directory[self.USER_FULL_DN])
        self.assertEqual(self.ldapobj.directory[self.USER_FULL_DN][settings.USER_LDAP_MAP["ldap_lock_time"]][0], "000001010000Z")

    @mock.patch('data_facility_admin.helpers.KeycloakHelper')
    def test_ldap_inactive_users_created_At(self, mock_keycloak):
        self.setUser(status=User.STATUS_NEW)

        ldap_helper = LDAPHelper()
        ldap_helper.export_users()

        self.setUser(created_at=timezone.now() - datetime.timedelta(60, 0, 0))
        
        ldap_helper.export_users()
        
        self.assertEqual(User.STATUS_LOCKED_INACTIVITY, User.objects.filter(ldap_id=self.USER_LDAP_ID)[0].status)

        self.assertIn(settings.USER_LDAP_MAP["ldap_lock_time"], self.ldapobj.directory[self.USER_FULL_DN])
        self.assertEqual(self.ldapobj.directory[self.USER_FULL_DN][settings.USER_LDAP_MAP["ldap_lock_time"]][0], "000001010000Z")
