#!/usr/bin/python
# -*- coding: utf-8 -*-

''' DFAdmin django tests '''
from data_facility_admin.models import *
from django.db import IntegrityError
from django.test import Client, TestCase
# from django.test import SimpleTestCase
from django.utils import timezone

from data_facility_admin import models

# pylint: disable:too-few-public-methods
USERNAME = 'danielcastellani'
YESTERDAY = timezone.now() - timezone.timedelta(days=1)
TOMORROW = timezone.now() + timezone.timedelta(days=1)

class DatabaseTests(TestCase):
    ''' Basic Database tests.'''

    def test_df_role_name_must_be_unique(self):
        role_name = 'Test Role Name'
        DfRole.objects.create(name=role_name)
        self.assertRaises(IntegrityError, DfRole.objects.create, name=role_name)

    def test_usersame_correctly_generated(self):
        user = models.User.objects.create(first_name='Daniel', last_name="Castellani")
        self.assertEqual(USERNAME, user.ldap_name)
        self.assertEqual(USERNAME, user.username)

    def test_save_multiple_users_with_same_name(self):
        u1 = User(first_name='daniel', last_name='castellani', email='dcastellani1@adrf.info')
        u2 = User(first_name='daniel', last_name='castellani', email='dcastellani2@adrf.info')
        u3 = User(first_name='daniel', last_name='castellani', email='dcastellani3@adrf.info')

        u1.save()
        u2.save()
        u3.save()

        self.assertNotEqual(u1.ldap_name, u2.ldap_name)
        self.assertNotEqual(u3.ldap_name, u2.ldap_name)
        self.assertNotEqual(u1.ldap_name, u3.ldap_name)

    def test_save_multiple_projects_with_same_name(self):
        p1 = Project(name='test')
        p2 = Project(name='test')
        p3 = Project(name='test')

        p1.save()
        p2.save()
        p3.save()

        self.assertNotEqual(p1.ldap_name, p2.ldap_name)
        self.assertNotEqual(p3.ldap_name, p2.ldap_name)
        self.assertNotEqual(p1.ldap_name, p3.ldap_name)

    def test_save_multiple_datasets_with_same_name(self):
        o1 = Dataset(name='test', dataset_id='1')
        o1.save()
        o2 = Dataset(name='test', dataset_id='2')
        o2.save()
        o3 = Dataset(name='test', dataset_id='3')
        o3.save()

        self.assertNotEqual(o1.ldap_name, o2.ldap_name)
        self.assertNotEqual(o3.ldap_name, o2.ldap_name)
        self.assertNotEqual(o1.ldap_name, o3.ldap_name)


class DatasetTests(TestCase):
    ''' Dataset Logic tests.'''

    def test_dataset_expired_system_status_is_disabled_when_disabled(self):
        dataset = Dataset(status=Dataset.STATUS_DISABLED,
                          expiration=YESTERDAY)
        assert dataset.system_status() is Dataset.STATUS_DISABLED

    def test_dataset_expired_system_status_is_disabled_when_active(self):
        dataset = Dataset(status=Dataset.STATUS_ACTIVE,
                          expiration=YESTERDAY)
        assert dataset.system_status() is Dataset.STATUS_DISABLED

    def test_dataset_not_expired_system_status_is_active_when_active(self):
        dataset = Dataset(status=Dataset.STATUS_ACTIVE,
                          expiration=TOMORROW)
        assert dataset.system_status() is Dataset.STATUS_ACTIVE

    def test_dataset_not_expired_system_status_is_disabled_when_disabled(self):
        dataset = Dataset(status=Dataset.STATUS_DISABLED,
                          expiration=TOMORROW)
        assert dataset.system_status() is Dataset.STATUS_DISABLED


class DatasetAccessTests(TestCase):
    ''' DataAccess Logic tests.'''

    def test_data_access_should_be_disabled_when_dataset_is_disabled(self):
        dataset = Dataset(status=Dataset.STATUS_DISABLED,
                          expiration=TOMORROW)
        data_access = DatasetAccess(dataset=dataset)
        assert data_access.status() is Dataset.STATUS_DISABLED


class LdapObjectrTests(TestCase):
    ''' User logic tests.'''

    def test_normalize_ldap_name(self):
        lo = LdapObject(ldap_name=u"á é í ó â ê î ô û ú")
        lo.prepare_ldap_name()
        self.assertEqual('aeioaeiouu', lo.ldap_name)

    def test_ldap_name_remove_spaces(self):
        lo = LdapObject(ldap_name='a b')
        lo.prepare_ldap_name()
        self.assertEqual('ab', lo.ldap_name)


class UserTests(TestCase):
    ''' User logic tests.'''

    def test_username_collision_case_1(self):
        User.objects.create(ldap_name='testuser1', email='a1@a.a')
        User.objects.create(ldap_name='testuser2', email='a2@a.a')
        u = User.objects.create(ldap_name='testuser', email='a@a.a')
        self.assertEqual('testuser', u.ldap_name)

    def test_username_collision_case_2(self):
        User.objects.create(ldap_name='testuser-1', email='a1@a.a')
        u = User.objects.create(ldap_name='testuser')
        self.assertEqual('testuser', u.ldap_name)

    def test_username_collision_case_3(self):
        User.objects.create(ldap_name='atestuser', email='a@a.a')
        User.objects.create(ldap_name='atestuser1', email='a1@a.a')
        User.objects.create(ldap_name='atestuser2', email='a2@a.a')
        u = User.objects.create(ldap_name='atestuser', email='a3@a.a')
        # for u in User.objects.all(): print u.ldap_name
        self.assertEqual('atestuser3', u.ldap_name)

    def test_username_for_foreign_nationals(self):
        user = User.objects.create(first_name='John', last_name='Doe', foreign_national=True)
        expected_username = (user.first_name + user.last_name + '_fr').lower()
        self.assertEqual(expected_username, user.ldap_name)

    def test_username_for_contractors(self):
        user = User.objects.create(first_name='John', last_name='Doe', contractor=True)
        expected_username = (user.first_name + user.last_name + '_ctr').lower()
        self.assertEqual(expected_username, user.ldap_name)


def create_project_with_membership_permission_for_test(system_role):
    p = Project.objects.create(name='test_memberships')
    user = User.objects.create(first_name='first_name', last_name='last_name',
                               ldap_name='test-user', email='a@a.a', status=User.STATUS_ACTIVE)
    role = ProjectRole.objects.create(name='admin', system_role=system_role)
    pm = ProjectMember.objects.create(member=user, project=p, role=role, start_date=YESTERDAY, end_date=TOMORROW)
    p.projectmember_set.add(pm)

    p.refresh_from_db()
    return p, user, role, pm


class ProjectTests(TestCase):
    ''' Project Logic tests.'''

    def test_project_name_collision_case_1(self):
        Project.objects.create(name='ada_pub_1')
        Project.objects.create(name='ada_pub_1')
        p = Project.objects.create(name='ada_pub')
        self.assertEqual('project-ada_pub', p.ldap_name)

    def test_hyphens_should_turn_into_underline_on_ldap_name(self):
        p = Project.objects.create(name='ada-pub')
        self.assertEqual('project-ada_pub', p.ldap_name)

    def test_spaces_should_turn_into_underline_on_ldap_name(self):
        p = Project.objects.create(name='ada pub')
        self.assertEqual('project-ada_pub', p.ldap_name)

    def test_instructor_permissions_override_membership_permissions(self):
        instructor_user_username = 'instructor_user'
        instructor_user = User(ldap_name=instructor_user_username,
                               email=instructor_user_username + '@adrf.test',
                               status=User.STATUS_ACTIVE)
        instructor_user.save()
        instructors = DfRole(name='instructor_users-test')
        instructors.save()
        UserDfRole.objects.create(role=instructors,
                                  user=instructor_user,
                                  begin=timezone.now()).save()
        p = Project.objects.create(name='test-permissions',
                                   instructors=instructors,
                                   status=Project.STATUS_ACTIVE)
        user_permission = p.active_member_permissions()[0]
        self.assertEqual(ProjectRole.SYSTEM_ROLE_WRITER, user_permission['system_role'])

    def test_empty_project_has_no_active_member_permissions(self):
        active_members = Project.objects.create(name='test_memberships').active_members()
        assert len(active_members) is 0

    def test_active_member_has_project_role_admin(self):
        p, user, role, pm = create_project_with_membership_permission_for_test(ProjectRole.SYSTEM_ROLE_ADMIN)
        active_members = p.active_members()
        assert len(active_members) is 1
        assert user in active_members

    def test_active_member_has_project_role_reader(self):
        p, user, role, pm = create_project_with_membership_permission_for_test(ProjectRole.SYSTEM_ROLE_READER)
        active_members = p.active_members()
        assert len(active_members) is 1
        assert user in active_members

    def test_active_member_has_project_role_writer(self):
        p, user, role, pm = create_project_with_membership_permission_for_test(ProjectRole.SYSTEM_ROLE_WRITER)
        active_members = p.active_members()
        assert len(active_members) is 1
        assert user in active_members

    def test_active_member_permissions_has_project_role_admin(self):
        p, user, role, pm = create_project_with_membership_permission_for_test(ProjectRole.SYSTEM_ROLE_ADMIN)
        active_member_permissions = p.active_member_permissions()
        assert len(active_member_permissions) is 1
        self.assertEqual(active_member_permissions[0]['system_role'], ProjectRole.SYSTEM_ROLE_ADMIN)

    def test_active_member_permissions_has_project_role_reader(self):
        p, user, role, pm = create_project_with_membership_permission_for_test(ProjectRole.SYSTEM_ROLE_READER)
        active_member_permissions = p.active_member_permissions()
        assert len(active_member_permissions) is 1
        self.assertEqual(active_member_permissions[0]['system_role'], ProjectRole.SYSTEM_ROLE_READER)

    def test_active_member_permissions_has_project_role_writer(self):
        p, user, role, pm = create_project_with_membership_permission_for_test(ProjectRole.SYSTEM_ROLE_WRITER)
        active_member_permissions = p.active_member_permissions()
        assert len(active_member_permissions) is 1
        self.assertEqual(active_member_permissions[0]['system_role'], ProjectRole.SYSTEM_ROLE_WRITER)


class ProjectMemberTests(TestCase):
    ''' ProjectMember Logic tests.'''

    @staticmethod
    def test_membership_is_not_active_without_start_date():
        membership = ProjectMember(start_date=None, end_date=TOMORROW, member=User(status=User.STATUS_ACTIVE))
        assert membership.active() is False

    @staticmethod
    def test_membership_is_active_without_end_date():
        membership = ProjectMember(start_date=YESTERDAY, end_date=None, member=User(status=User.STATUS_ACTIVE))
        assert membership.active() is True

    @staticmethod
    def test_membership_is_active_with_start_date_in_the_past():
        membership = ProjectMember(start_date=YESTERDAY, end_date=TOMORROW, member=User(status=User.STATUS_ACTIVE))
        assert membership.active()

    @staticmethod
    def test_membership_is_not_active_with_start_date_in_the_future():
        membership = ProjectMember(start_date=TOMORROW, end_date=TOMORROW, member=User(status=User.STATUS_ACTIVE))
        assert membership.active() is False

    @staticmethod
    def test_membership_is_active_with_end_date_in_the_future():
        membership = ProjectMember(start_date=YESTERDAY, end_date=TOMORROW, member=User(status=User.STATUS_ACTIVE))
        assert membership.active()

    @staticmethod
    def test_membership_is_not_active_with_end_date_in_the_past():
        membership = ProjectMember(start_date=YESTERDAY, end_date=YESTERDAY, member=User(status=User.STATUS_ACTIVE))
        assert membership.active() is False

    @staticmethod
    def test_membership_is_active_with_start_date_in_the_past_and_end_date_in_the_future():
        membership = ProjectMember(start_date=YESTERDAY, end_date=TOMORROW, member=User(status=User.STATUS_ACTIVE))
        assert membership.active()
