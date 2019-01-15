from django.test import TestCase

from data_facility_admin.factories import DatasetAccessFactory
from data_facility_admin.models import DatasetAccess
from .factories import UserFactory, DatasetFactory, ProjectFactory
from .models import User
from scripts import daily_notification
import datetime
from django.utils import timezone


# pylint: disable=too-many-public-methods
class DailyNotificationTests(TestCase):
    ''' Basic List and Add admin tests.'''

    NOW = timezone.localtime(timezone.now())
    @classmethod
    def setUpClass(cls):
        super(DailyNotificationTests, cls).setUpClass()

    def test_system_update_has_users_created(self):
        user = UserFactory.create()
        system_updates = daily_notification.get_system_updates(DailyNotificationTests.NOW)
        self.assertEqual([str(user)], system_updates['users_created'])

    def test_system_update_has_users_updated(self):
        user = UserFactory.create()
        user.status = User.STATUS_DISABLED
        user.save()
        system_updates = daily_notification.get_system_updates(DailyNotificationTests.NOW)
        self.assertEqual([str(user)], system_updates['users_updated'])

    def test_system_update_has_users_pwd_expired(self):
        user = UserFactory.build()
        user.ldap_last_pwd_change = DailyNotificationTests.NOW - datetime.timedelta(days=61)
        user.save()
        system_updates = daily_notification.get_system_updates(DailyNotificationTests.NOW)
        self.assertEqual([str(user)], system_updates['users_pwd_expired'])

    def test_system_update_has_datasets_created(self):
        dataset = DatasetFactory.create()
        system_updates = daily_notification.get_system_updates(DailyNotificationTests.NOW)
        self.assertEqual([str(dataset)], system_updates['datasets_created'])

    def test_system_update_has_datasets_updated(self):
        dataset = DatasetFactory.create()
        dataset.name = 'new name'
        dataset.save()
        system_updates = daily_notification.get_system_updates(DailyNotificationTests.NOW)
        self.assertEqual([str(dataset)], system_updates['datasets_updated'])

    def test_system_update_has_projects_created(self):
        project = ProjectFactory.create()
        system_updates = daily_notification.get_system_updates(DailyNotificationTests.NOW)
        self.assertEqual([str(project)], system_updates['projects_created'])

    def test_system_update_has_projects_updated(self):
        project = ProjectFactory.create()
        project.name = 'new name'
        project.save()
        system_updates = daily_notification.get_system_updates(DailyNotificationTests.NOW)
        self.assertEqual([str(project)], system_updates['projects_updated'])

    def test_system_update_has_data_access_created(self):
        data_access = DatasetAccessFactory.create()
        system_updates = daily_notification.get_system_updates(DailyNotificationTests.NOW)
        self.assertEqual([str(data_access)], system_updates['access_created'])

    def test_system_update_has_data_access_updated(self):
        data_access = DatasetAccessFactory.create()
        data_access.expire_at = DailyNotificationTests.NOW
        data_access.save()
        system_updates = daily_notification.get_system_updates(DailyNotificationTests.NOW)
        self.assertEqual([str(data_access)], system_updates['access_updated'])

    def test_update_period_reference_today_if_no_parameter(self):
        ref_date = daily_notification.update_period(None)
        self.assertIsNotNone(ref_date)
        correct = timezone.localtime(timezone.now()) - datetime.timedelta(days=1)
        self.assertEqual(correct.year, ref_date.year)
        self.assertEqual(correct.month, ref_date.month)
        self.assertEqual(correct.day, ref_date.day)


