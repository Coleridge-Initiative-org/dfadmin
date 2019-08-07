from django_filters import filters
from rest_framework import mixins, generics, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.utils import timezone

from data_facility_admin.models import User
from .. import models
from . import serializers
from django.shortcuts import get_object_or_404

import logging
# from django_filters import rest_framework as filters
from django.db.models import Q

logger = logging.getLogger(__name__)


# TODO: Add API versioning: https://www.django-rest-framework.org/api-guide/versioning/


class DfRoleViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = models.DfRole.objects.all().order_by('name')
    serializer_class = serializers.DfRoleSerializer
    lookup_field = 'ldap_name'
    # lookup_url_kwarg = 'ldap_name'


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Search based on name.
    """
    queryset = models.Category.objects.all().order_by('dataset_id')
    serializer_class = serializers.CategorySerializer
    search_fields = ('name')
    ordering = ('name',)


class DatasetViewSet(viewsets.ModelViewSet):
    """
    Search is based on 'name', 'dataset_id', 'data_provider__name', 'description'.

    Additional filters:
        - access_type: Public (Green), Restricted (Restricted Green) or Private (Yellow)
        - category__name: name of the category. Can be a single value or multiple '|' separated.
        - data_provider__name: name of the data provider. Can be a single value or multiple '|' separated.
        - start_date and end_date: to filter datasets by temporal_coverage
    """
    # filter_backends = (filters.DjangoFilterBackend,)
    serializer_class = serializers.DatasetSerializer
    filter_fields = ('dataset_id',
                     'name',
                     'public',
                     'data_classification',
                     )
    # filterset_fields = ('category__name',)
    # filterset_fields = {'category__name': ['exact']}

    # filterset_fields = {'dataset_id': ['exact'],
    #                     'name': ['exact'],
    #                     'public': ['exact'],
    #                     'data_classification': ['exact'],
    #                     'category__name': ['exact'],
    #                     'data_provider__name': ['exact'],
    #                     'temporal_coverage_start__year': ['gte'],
    #                     'temporal_coverage_end__year': ['lte']}
    search_fields = ('name', 'dataset_id', 'data_provider__name', 'description')
    ordering = ('name',)
    ordering_fields = ('name', 'dataset_id')
    lookup_field = 'dataset_id'
    lookup_url_kwarg = 'dataset_id'

    def get_queryset(self):
        """
        Retrieve datasets respecting ACLs.
        """
        queryset = models.Dataset.objects.filter(available=True)
        access_type = self.request.query_params.get('access_type', None)
        logger.debug('Access_type filter: %s' % access_type)
        if access_type:
            from data_facility_admin import metadata_serializer
            data_classification = metadata_serializer.data_classification_to_model(access_type)
            logger.debug('Filter queryset also by data classification = %s' % data_classification)
            queryset = queryset.filter(data_classification=data_classification)
            logger.debug('QUERYSET.query=%s' % queryset.query)

        # Categories
        if self.request.query_params.get('category__name', None):
            categories = self.request.query_params.get('category__name', '').split('|')
            q_filter = None
            for c in categories:
                q_filter = q_filter | Q(category__name=c) if q_filter else Q(category__name=c)
            queryset = queryset.filter(q_filter)

        # Data Provider
        if self.request.query_params.get('data_provider__name', None):
            providers = self.request.query_params.get('data_provider__name', '').split('|')
            q_filter = None
            for c in providers:
                q_filter = q_filter | Q(data_provider__name=c) if q_filter else Q(data_provider__name=c)
            queryset = queryset.filter(q_filter)

        # Start and End Date
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(temporal_coverage_start__year__gte=int(start_date))
        if end_date:
            queryset = queryset.filter(temporal_coverage_end__year__lte=int(end_date))

        request_user = self.request.user
        logger.debug('Current user: %s' % request_user)

        return queryset


class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    lookup_field = 'ldap_name'
    lookup_url_kwarg = 'username'
    STATUS_WHITELIST = models.User.MEMBERSHIP_STATUS_WHITELIST
    queryset = models.User.objects.filter(status__in=STATUS_WHITELIST).order_by('ldap_name')
    serializer_class = serializers.UserSerializer
    filter_fields = ('first_name', 'last_name', 'email', 'ldap_name')
    search_fields = ('first_name', 'last_name',)
    ordering_fields = ('first_name', 'last_name',)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    # queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    filter_fields = ('name', 'status', 'has_irb', 'owner', 'type', 'ldap_name')
    search_fields = ('name', 'owner__first_name', 'owner__last_name',
                     'owner__ldap_name', 'methodology', 'abstract',
                     'outcomes', 'mission',
                     'projectmember__member__ldap_name',
                     # 'projectmember__member__first_name',
                     # 'projectmember__member__last_name',
                     )
    ordering_fields = ('name', 'owner',)
    lookup_field = 'ldap_name'
    # lookup_url_kwarg = 'ldap_name'

    def get_queryset(self):
        """
        Retrieve datasets respecting ACLs.
        """
        queryset = models.Project.objects.filter(models.Project.FILTER_ACTIVE)
        user_filter = self.request.query_params.get('member', None) or self.request.query_params.get('user', None)
        logger.debug('member filter: %s' % user_filter)
        # member
        curator = False
        if user_filter:
            now = timezone.now()
            queryset = queryset.filter(Q(projectmember__member__ldap_name=user_filter) |
                                       Q(instructors__userdfrole__user__ldap_name=user_filter))
            # Filter expired or not started projects
            queryset = queryset.filter(Q(projectmember__project__start__isnull=True) |
                                       Q(projectmember__project__start__lte=now))
            # Filter with invalid membership
            queryset = queryset.filter(Q(projectmember__project__end__isnull=True) |
                                       Q(projectmember__project__end__gte=now))
            queryset = queryset.filter(projectmember__start_date__lte=now,
                                       projectmember__end_date__gte=now)
            queryset = queryset.distinct()

        # TODO: Remove DATA TRANSFER filtering when new PG_SYNC is in place.
        # type
        type_filter = self.request.query_params.get('type', None)
        logger.debug('type filter: %s' % type_filter)
        if not type_filter:     # Add default filter only when there is no type param and the user is not a Data Curator
            data_curator = False
            if user_filter:
                user_roles = [dfr.name for dfr in models.User.objects.get(ldap_name=user_filter).active_roles]
                data_curator = models.DfRole.ADRF_CURATORS in user_roles
            if not data_curator:
                queryset = queryset.exclude(type=models.Project.PROJECT_TYPE_DATA_TRANSFER)

        request_user = self.request.user
        logger.debug('Current user: %s' % request_user)

        return queryset


class DataStewardViewSet(viewsets.ModelViewSet):
    queryset = models.DataSteward.objects.all()
    serializer_class = serializers.DataStewardSerializer
    filter_fields = '__all__'
    search_fields = '__all__'
    # ordering_fields = ('name', 'owner', )


class DataProviderViewSet(viewsets.ModelViewSet):
    queryset = models.DataProvider.objects.all()
    serializer_class = serializers.DataProviderSerializer
    filter_fields = '__all__'
    search_fields = '__all__'
    # ordering_fields = ('name', 'owner', )
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'


DatabaseSyncListView = ListAPIView.as_view(queryset=models.Project.objects.all(),
                                           serializer_class=serializers.DatabaseSyncSerializer)
