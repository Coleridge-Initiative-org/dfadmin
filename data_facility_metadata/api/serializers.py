from .. import models
from rest_framework import serializers


class FileFormatSerializer(serializers.HyperlinkedModelSerializer):
    # owner = serializers.ReadOnlyField(source='owner.username')
    # parent_project_ldap_name = serializers.ReadOnlyField(source='parent_project.ldap_name')

    class Meta:
        model = models.FileFormat
        fields = '__all__'


class FileSerializer(serializers.HyperlinkedModelSerializer):
    type = serializers.HyperlinkedRelatedField(many=False, view_name='fileformat-detail', read_only=True)

    class Meta:
        model = models.File
        fields = '__all__'
        depth = 1


class DataTableSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.DataTable
        fields = '__all__'
        # depth = 1


class StorageTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.StorageType
        fields = '__all__'


class DataStoreSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.DataStore
        fields = '__all__'


class PhysicalDataTableSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.PhysicalDataTable
        fields = '__all__'


class DataTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.DataType
        fields = '__all__'


class VariableSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Variable
        fields = '__all__'


class ValueSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Value
        fields = '__all__'
