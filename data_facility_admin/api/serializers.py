from rest_framework.relations import PrimaryKeyRelatedField

from ..models import Project, User, DfRole, Dataset, DataSteward, DataProvider, Category, ProjectTool
from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin
import logging
logger = logging.getLogger(__name__)


class DFAdminModelSerializerWithId(serializers.ModelSerializer):
    """Extend the HyperlinkedModelSerializer to add IDs as well for the best of
    both worlds.
    """
    id = serializers.ReadOnlyField()


class DatabaseSyncSerializer(DynamicFieldsMixin, DFAdminModelSerializerWithId):
    owner = serializers.ReadOnlyField(source='owner.username')
    parent_project_ldap_name = serializers.ReadOnlyField(source='parent_project.ldap_name')
    dfri = serializers.ReadOnlyField(source='ldap_name')

    class Meta:
        model = Project
        fields = ('name',
                  'ldap_name',
                  'environment',
                  'status',
                  'parent_project_ldap_name',
                  # 'parent_project',
                  'owner',
                  # 'type',
                  'members_count',
                  'active_member_permissions',
                  'datasets_with_access',
                  'db_schema',
                  'instructors',
                  'dfri',
                  )


class UserSerializer(DynamicFieldsMixin, DFAdminModelSerializerWithId):
    username = serializers.ReadOnlyField(source='ldap_name')
    avatar_url = serializers.ReadOnlyField(source='avatar')

    class Meta:
        model = User
        # fields = ('first_name', 'last_name', 'full_name',
        #           'username', 'email', 'job_title', 'affiliation', 'avatar', 'id', 'url')
        fields = '__all__'


class DfRoleSerializer(DynamicFieldsMixin, DFAdminModelSerializerWithId):
    active_users = serializers.HyperlinkedRelatedField(many=True, view_name='user-detail', read_only=True, lookup_field='username')

    class Meta:
        model = DfRole
        fields = ('name', 'description', 'active_users', 'active_usernames')
        # fields = '__all__'


class DataProviderSerializer(DynamicFieldsMixin, DFAdminModelSerializerWithId):
    # dataset = serializers.HyperlinkedRelatedField(many=True, view_name='dataset-detail',
    #                                               read_only=True, lookup_field='dataset_id')

    class Meta:
        model = DataProvider
        fields = '__all__'


class CategorySerializer(DynamicFieldsMixin, DFAdminModelSerializerWithId):
    class Meta:
        model = Category
        fields = '__all__'


class DatasetSerializer(DynamicFieldsMixin, DFAdminModelSerializerWithId):
    INCLUDE_DETAILS = 'include_detailed_metadata'

    category = CategorySerializer()
    db_schema = serializers.ReadOnlyField(source='db_schema_name')
    adrf_id = serializers.ReadOnlyField(source='ldap_name')
    data_provider_name = serializers.ReadOnlyField(source='data_provider__name')
    db_schema_public = serializers.ReadOnlyField(source='database_schema.public')
    active_stewards = serializers.HyperlinkedRelatedField(many=True, view_name='user-detail', read_only=True, lookup_field='username')
    # data_provider = DataProviderSerializer(many=False)
    # data_provider = serializers.HyperlinkedRelatedField(many=False,
    #                                                     view_name='dataprovider-detail',
    #                                                     read_only=True,
                                                        # lookup_field='name'
                                                        # )

    class Meta:
        model = Dataset
        fields = ('dataset_id', 'name', 'description', 'dataset_citation', 'version',
                  'category',
                  'storage_location', 'available',
                  'expiration', 'data_classification', 'access_type', 'report_frequency',
                  'created_at', 'updated_at', 'expiration', 'temporal_coverage_start', 'temporal_coverage_end',
                  'data_ingested_at', 'data_updated_at',
                  'adrf_id', 'db_schema', 'db_schema_public', 'curator_permissions',
                  'public', 'data_provider_name', 'status', 'active_stewards',
                  'search_metadata', 'detailed_metadata')
        # fields = '__all__'


class ProjectToolSerializer(DynamicFieldsMixin, DFAdminModelSerializerWithId):
    related_projects = serializers.HyperlinkedRelatedField(many=False, view_name='project-detail', read_only=True, lookup_field='ldap_name')

    class Meta:
        model = ProjectTool
        fields = ('tool_name', 'other_name', 'notes', 'system_info', 'additional_info')


class ProjectSerializer(DynamicFieldsMixin, DFAdminModelSerializerWithId):
    # project_id = serializers.ReadOnlyField(source='ldap_name')

    # owner = serializers.HyperlinkedRelatedField(many=False, view_name='user-detail',
    #                                             read_only=True, lookup_field='username')
    owner = serializers.HyperlinkedRelatedField(many=False, view_name='user-detail', read_only=True, lookup_field='username')
    # owner = UserSerializer(many=False, read_only=True)
    # active_members = serializers.HyperlinkedRelatedField(many=True, view_name='user-detail',
    #                                                      read_only=True, lookup_field='username')
    active_members = UserSerializer(many=True, read_only=True)

    owner_username = serializers.ReadOnlyField(source='owner__ldap_name')
    # tools = PrimaryKeyRelatedField(queryset=ProjectTool.objects.all())
    related_tools = ProjectToolSerializer(many=True, read_only=True)

    #Fix to You may have failed to include the related model in your API,
    # or incorrectly configured the `lookup_field` attribute on this field.
    url = serializers.HyperlinkedIdentityField(view_name='project-detail', source='ldap_name',
                                               lookup_url_kwarg='ldap_name', lookup_field='ldap_name')

    class Meta:
        model = Project
        fields = ('name',
                  'type',
                  'requester',
                  'abstract',
                  'owner',
                  'methodology',
                  'mission',
                  'outcomes',
                  'mission',
                  'has_irb',
                  'status',
                  'url',
                  'id',
                  'owner_username',
                  'active_members',
                  'active_member_permissions',
                  'datasets_with_access',
                  'created_at',
                  'updated_at',
                  'tools',
                  'related_tools',
                  'ldap_name',
                  # 'project_id'
                  )
        # fields = '__all__'


    # TODO: fix project creation
    # def create(self, validated_data):
    #     logger.debug('Create called with params: %s' % validated_data)
    #     project = Project(**validated_data)
    #     logger.debug('project: %s' % project)
    #
    #     return project


class DataStewardSerializer(DFAdminModelSerializerWithId):

    class Meta:
        model = DataSteward
        fields = '__all__'





