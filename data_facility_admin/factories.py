from factory.django import DjangoModelFactory
import factory
from django.utils import timezone
from . import models


class UserFactory(DjangoModelFactory):
    class Meta:
        model = models.User
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    affiliation = factory.Faker('company')
    job_title = factory.Faker('job')
    email = factory.LazyAttribute(lambda a: '{0}.{1}@example.com'.format(a.first_name, a.last_name).lower())
    # ldap_name = factory.LazyAttribute(lambda a: '{0}{1}'.format(a.first_name, a.last_name).lower())


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = models.Project
    name = factory.Faker('job')
    abstract = factory.Faker('job')


class DatasetFactory(DjangoModelFactory):
    class Meta:
        model = models.Dataset
    name = factory.Faker('company')
    dataset_id = factory.Sequence(lambda n: 'ADRF-%s' % n)


class DatasetAccessFactory(DjangoModelFactory):
    class Meta:
        model = models.DatasetAccess
    project = factory.SubFactory(ProjectFactory)
    dataset = factory.SubFactory(DatasetFactory)
    start_at = factory.LazyFunction(lambda: timezone.now())


class DfRoleFactory(DjangoModelFactory):
    class Meta:
        model = models.DfRole
    name = factory.Faker('job')
    description = factory.Faker('job')
