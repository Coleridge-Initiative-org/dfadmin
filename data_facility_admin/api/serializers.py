from ..models import Project, User, DfRole, Dataset, DataSteward, DataProvider
from rest_framework import serializers
import logging
logger = logging.getLogger(__name__)


class HyperlinkedModelSerializerWithId(serializers.HyperlinkedModelSerializer):
    """Extend the HyperlinkedModelSerializer to add IDs as well for the best of
    both worlds.
    """
    id = serializers.ReadOnlyField()


class DatabaseSyncSerializer(HyperlinkedModelSerializerWithId):
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


class UserSerializer(HyperlinkedModelSerializerWithId):
    username = serializers.ReadOnlyField(source='ldap_name')
    class Meta:
        model = User
        # fields = ('first_name', 'last_name', 'full_name',
        #           'username', 'email', 'job_title', 'affiliation', 'avatar', 'id', 'url')
        fields = '__all__'


class DfRoleSerializer(HyperlinkedModelSerializerWithId):
    active_users = serializers.HyperlinkedRelatedField(many=True, view_name='user-detail', read_only=True)

    class Meta:
        model = DfRole
        fields = ('name', 'description', 'active_users', 'active_usernames')
        # fields = '__all__'


class DataProviderSerializer(HyperlinkedModelSerializerWithId):
    # dataset = serializers.HyperlinkedRelatedField(many=True, view_name='dataset-detail', read_only=True)

    class Meta:
        model = DataProvider
        fields = '__all__'


class DatasetSerializer(HyperlinkedModelSerializerWithId):
    db_schema = serializers.ReadOnlyField(source='db_schema_name')
    adrf_id = serializers.ReadOnlyField(source='ldap_name')
    db_schema_public = serializers.ReadOnlyField(source='database_schema.public')
    active_stewards = UserSerializer(many=True, read_only=True)
    # data_provider = DataProviderSerializer(many=False)
    # data_provider = serializers.HyperlinkedRelatedField(many=False, view_name='dataprovider-detail', read_only=True,
    #                                                     lookup_field='name')

    class Meta:
        model = Dataset
        fields = ('dataset_id', 'name', 'description', 'dataset_citation', 'version', 'storage_location', 'shareable',
                  'expiration', 'data_classification', 'report_frequency',
                  'created_at', 'updated_at', 'expiration', 'temporal_coverage_start', 'temporal_coverage_end',
                  'data_ingested_at', 'data_updated_at',
                  'adrf_id', 'db_schema', 'db_schema_public', 'curator_permissions',
                  'public', 'data_provider', 'status', 'active_stewards',
                  'id', 'url', 'search_gmeta', 'detailed_gmeta')
        # fields = '__all__'


class ProjectSerializer(HyperlinkedModelSerializerWithId):
    owner = serializers.HyperlinkedRelatedField(many=False, view_name='user-detail', read_only=True)
    active_members = serializers.HyperlinkedRelatedField(many=True, view_name='user-detail', read_only=True)
    owner_username = serializers.ReadOnlyField(source='owner__ldap_name')

    class Meta:
        model = Project
        fields = ('name',
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
                  )
        # fields = '__all__'


    def create(self, validated_data):
        logger.debug('Create called with params: %s' % validated_data)
        project = Project(**validated_data)
        logger.debug('project: %s' % project)

        return project


class DataStewardSerializer(HyperlinkedModelSerializerWithId):

    class Meta:
        model = DataSteward
        fields = '__all__'





