from rest_framework import mixins, generics, viewsets
from rest_framework.generics import ListAPIView
from .. import models
from . import serializers

# TODO: Add API versioning: https://www.django-rest-framework.org/api-guide/versioning/


class DfRoleViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = models.DfRole.objects.all().order_by('name')
    serializer_class = serializers.DfRoleSerializer
    lookup_field = 'ldap_name'
    # lookup_url_kwarg = 'ldap_name'


class DatasetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = models.Dataset.objects.all().order_by('dataset_id')
    serializer_class = serializers.DatasetSerializer
    filter_fields = ('dataset_id', 'name', 'public', 'data_provider', 'data_classification')
    search_fields = ('name', 'dataset_id', 'data_provider', 'description')
    ordering_fields = ('name', 'dataset_id')
    lookup_field = 'dataset_id'
    lookup_url_kwarg = 'dataset_id'


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
    ordering_fields = ('first_name', 'last_name', )


class ProjectViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    filter_fields = ('name', 'status', 'has_irb', 'owner')
    search_fields = ('name', 'owner__first_name', 'owner__last_name', 'owner__ldap_name', 'methodology', 'abstract',
                     'outcomes', 'mission',
                     'projectmember__member__ldap_name',
                     'projectmember__member__first_name',
                     'projectmember__member__last_name',
                     )
    ordering_fields = ('name', 'owner', )


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
