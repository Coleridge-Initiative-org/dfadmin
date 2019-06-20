''' DFAdmin django tests '''
from django.test import Client, TestCase

from data_facility_admin.models import *
from data_facility_admin.factories import *
from datetime import date, timedelta


YESTERDAY = timezone.now() - timedelta(days=1)
TOMORROW = timezone.now() + timedelta(days=1)

# pylint: disable=too-many-public-methods
class ProjectQueryTests(TestCase):
    ''' Basic List and Add admin tests.'''

    # @classmethod
    # def setUpClass(cls):
    #     super(ProjectQueryTests, cls).setUpClass()
    #
    # def setUp(self):

    def test_filter_active_with_status_active_returns_object(self):
        p = ProjectFactory.create(status=Project.STATUS_ACTIVE)
        results = Project.objects.filter(Project.FILTER_ACTIVE)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0], p)

    def test_filter_active_with_status_new_returns_nothing(self):
        p = ProjectFactory.create(status=Project.STATUS_NEW)
        results = Project.objects.filter(Project.FILTER_ACTIVE)
        self.assertEqual(len(results), 0)

    def test_filter_active_with_status_archived_returns_nothing(self):
        p = ProjectFactory.create(status=Project.STATUS_ARCHIVED)
        results = Project.objects.filter(Project.FILTER_ACTIVE)
        self.assertEqual(len(results), 0)

    def test_filter_active_with_start_null_returns_object(self):
        p = ProjectFactory.create(status=Project.STATUS_ACTIVE, start=None)
        results = Project.objects.filter(Project.FILTER_ACTIVE)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0], p)

    def test_filter_active_with_start_past_returns_object(self):
        p = ProjectFactory.create(status=Project.STATUS_ACTIVE, start=YESTERDAY)
        results = Project.objects.filter(Project.FILTER_ACTIVE)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0], p)

    def test_filter_active_with_start_future_returns_nothing(self):
        p = ProjectFactory.create(status=Project.STATUS_ACTIVE, start=TOMORROW)
        results = Project.objects.filter(Project.FILTER_ACTIVE)
        self.assertEqual(len(results), 0)

    def test_filter_active_with_end_null_returns_object(self):
        p = ProjectFactory.create(status=Project.STATUS_ACTIVE, end=None)
        results = Project.objects.filter(Project.FILTER_ACTIVE)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0], p)

    def test_filter_active_with_end_future_returns_object(self):
        p = ProjectFactory.create(status=Project.STATUS_ACTIVE, end=TOMORROW)
        results = Project.objects.filter(Project.FILTER_ACTIVE)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0], p)

    def test_filter_active_with_end_past_returns_nothing(self):
        p = ProjectFactory.create(status=Project.STATUS_ACTIVE, end=YESTERDAY)
        results = Project.objects.filter(Project.FILTER_ACTIVE)
        self.assertEqual(len(results), 0)


# pylint: disable=too-many-public-methods
class UserDfRoleQueryTests(TestCase):
    ''' Basic List and Add admin tests.'''

    # @classmethod
    # def setUpClass(cls):
    #     super(ProjectQueryTests, cls).setUpClass()

    def setUp(self):
        self.user = UserFactory.create()
        self.role = DfRole.objects.create(name='My Test Role')

    def test_filter_active_with_begin_past_returns_object(self):
        user_role = UserDfRole.objects.create(user=self.user, role=self.role, begin=YESTERDAY)
        results = UserDfRole.objects.filter(UserDfRole.FILTER_ACTIVE)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], user_role)

    def test_filter_active_with_begin_future_returns_nothing(self):
        user_role = UserDfRole.objects.create(user=self.user, role=self.role, begin=TOMORROW)
        results = UserDfRole.objects.filter(UserDfRole.FILTER_ACTIVE)
        self.assertEqual(len(results), 0)

    def test_filter_active_with_end_future_returns_object(self):
        user_role = UserDfRole.objects.create(user=self.user, role=self.role, begin=YESTERDAY, end=TOMORROW)
        results = UserDfRole.objects.filter(UserDfRole.FILTER_ACTIVE)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], user_role)

    def test_filter_active_with_end_past_returns_nothing(self):
        user_role = UserDfRole.objects.create(user=self.user, role=self.role, begin=YESTERDAY, end=YESTERDAY)
        results = UserDfRole.objects.filter(UserDfRole.FILTER_ACTIVE)
        self.assertEqual(len(results), 0)


