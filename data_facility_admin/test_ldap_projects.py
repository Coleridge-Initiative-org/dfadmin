from django.test import TestCase
from data_facility_admin.models import *
from data_facility_admin.helpers import LDAPHelper
import mock
from mockldap import MockLdap
from django.conf import settings
import ldap
from django.utils import timezone
from test_ldap import BaseLdapTestCase


class LdapProjectsTestCase(BaseLdapTestCase):
    PROJECT_LDAP_ID = LdapObject.MIN_LDAP_UID
    PROJECT_FULL_DN = 'cn=project-test,ou=projects,' + settings.LDAP_BASE_DN
    PROJECT_LDAP_BASE = "%s,%s" % (settings.LDAP_PROJECT_SEARCH, settings.LDAP_BASE_DN)

    def setUp(self):
        super(LdapProjectsTestCase, self).setUp()
        self.proj = Project(name='test', abstract='test', methodology='test', status=Project.STATUS_ACTIVE, type=Project.PROJECT_TYPE_CLASS)
        self.proj.save()

    @classmethod
    def create_user(cls, ldap_name=None, first_name="John",
                    last_name="Lennon",
                    email="johnlennon@adrf.info.dev",
                    status=User.STATUS_NEW,
                    ldap_last_auth_time=None,
                    ldap_lock_time=None,
                    ldap_last_pwd_change=None,
                    created_at=None,
                    updated_at=None,
                    system_user=False):

        u = User()
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
        return u

    def test_ldap_project_create_disable(self):
        self.assertTrue(len(Project.objects.all()) == 1, "The database should have only one project")

        ldap_helper = LDAPHelper()
        values = ldap_helper.flat_attributes_from_settings(settings.PROJECT_LDAP_MAP.values())
        self.ldapobj.search_s.seed(self.PROJECT_LDAP_BASE, ldap.SCOPE_SUBTREE, '(&(objectclass=posixGroup)(|(cn=project-*)(cn=yproject-*)))', values)([])

        LDAPHelper().export_projects()

        self.assertEqual(len([x for x in self.ldapobj.methods_called() if x == 'add_s']), 1, "The add_s method should have been called adding a new project")
        self.assertIn(self.PROJECT_FULL_DN, self.ldapobj.directory, "The project should have been inserted")

        self.proj.status = Project.STATUS_ARCHIVED
        self.proj.save()
        self.ldapobj.search_s.seed(self.PROJECT_LDAP_BASE, ldap.SCOPE_SUBTREE, '(&(objectclass=posixGroup)(|(cn=project-*)(cn=yproject-*)))', ['name', 'creationdate', 'gidNumber', 'member', 'cn', 'summary'])([(self.PROJECT_FULL_DN, self.ldapobj.directory[self.PROJECT_FULL_DN])])

        LDAPHelper().export_projects()

        self.assertIn('delete_s', self.ldapobj.methods_called() )

        self.assertNotIn(self.PROJECT_FULL_DN, self.ldapobj.directory, "The project should notbe in LDAP")

    @mock.patch('data_facility_admin.helpers.KeycloakHelper')
    def test_ldap_project_membership(self, mock_keycloak):
        self.assertTrue(len(Project.objects.all()) == 1, "The database should have only one project")

        ldap_helper = LDAPHelper()
        values = ldap_helper.flat_attributes_from_settings(settings.PROJECT_LDAP_MAP.values())
        self.ldapobj.search_s.seed(self.PROJECT_LDAP_BASE, ldap.SCOPE_SUBTREE, '(&(objectclass=posixGroup)(|(cn=project-*)(cn=yproject-*)))', values)([])

        ldap_helper.export_projects()

        self.assertEqual(len([x for x in self.ldapobj.methods_called() if x == 'add_s']), 1, "The add_s method should have been called adding a new project")
        self.assertIn(self.PROJECT_FULL_DN, self.ldapobj.directory, "The project should have been inserted")

        user = self.create_user()
        user.save()
        ldap_helper.export_users()
        user = User.objects.filter(ldap_name="johnlennon")[0]
        member_role = ProjectRole(name="Member", system_role=ProjectRole.SYSTEM_ROLE_READER)
        member_role.save()
        project_member = ProjectMember(member=user, role=member_role, project=self.proj,
                                       start_date=timezone.now(),
                                       end_date=timezone.now())
        project_member.save()

        self.ldapobj.search_s.seed(self.PROJECT_LDAP_BASE, ldap.SCOPE_SUBTREE, '(&(objectclass=posixGroup)(|(cn=project-*)(cn=yproject-*)))', ['name', 'creationdate', 'gidNumber', 'member', 'cn', 'summary'])([(self.PROJECT_FULL_DN, self.ldapobj.directory[self.PROJECT_FULL_DN])])

        LDAPHelper().export_projects()

        self.assertNotIn('member', self.ldapobj.directory[self.PROJECT_FULL_DN])
        project_member.start_date=timezone.now() - timezone.timedelta(days=1)
        project_member.end_date=timezone.now() + timezone.timedelta(days=1)
        project_member.save()

        ldap_helper.export_projects()

        self.ldapobj.search_s.seed(self.PROJECT_LDAP_BASE, ldap.SCOPE_SUBTREE, '(&(objectclass=posixGroup)(|(cn=project-*)(cn=yproject-*)))', ['name', 'creationdate', 'gidNumber', 'member', 'cn', 'summary'])([(self.PROJECT_FULL_DN, self.ldapobj.directory[self.PROJECT_FULL_DN])])
        self.assertIn('member', self.ldapobj.directory[self.PROJECT_FULL_DN])

        user.status=User.STATUS_LOCKED_BY_ADMIN
        user.save()
        ldap_helper.export_users()
        ldap_helper.export_projects()
        self.ldapobj.search_s.seed(self.PROJECT_LDAP_BASE, ldap.SCOPE_SUBTREE, '(&(objectclass=posixGroup)(|(cn=project-*)(cn=yproject-*)))', ['name', 'creationdate', 'gidNumber', 'member', 'cn', 'summary'])([(self.PROJECT_FULL_DN, self.ldapobj.directory[self.PROJECT_FULL_DN])])
        self.assertNotIn('member', self.ldapobj.directory[self.PROJECT_FULL_DN])

        user.status=User.STATUS_LOCKED_WRONG_PASSWD
        user.save()
        ldap_helper.export_users()
        ldap_helper.export_projects()
        self.ldapobj.search_s.seed(self.PROJECT_LDAP_BASE, ldap.SCOPE_SUBTREE, '(&(objectclass=posixGroup)(|(cn=project-*)(cn=yproject-*)))', ['name', 'creationdate', 'gidNumber', 'member', 'cn', 'summary'])([(self.PROJECT_FULL_DN, self.ldapobj.directory[self.PROJECT_FULL_DN])])
        self.assertIn('member', self.ldapobj.directory[self.PROJECT_FULL_DN])

        project_member.end_date=timezone.now()
        project_member.save()
        ldap_helper.export_projects()
        self.ldapobj.search_s.seed(self.PROJECT_LDAP_BASE, ldap.SCOPE_SUBTREE, '(&(objectclass=posixGroup)(|(cn=project-*)(cn=yproject-*)))', ['name', 'creationdate', 'gidNumber', 'member', 'cn', 'summary'])([(self.PROJECT_FULL_DN, self.ldapobj.directory[self.PROJECT_FULL_DN])])
        self.assertNotIn('member', self.ldapobj.directory[self.PROJECT_FULL_DN])


