from .. import models
from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin


class FileFormatSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    # owner = serializers.ReadOnlyField(source='owner.username')
    # parent_project_ldap_name = serializers.ReadOnlyField(source='parent_project.ldap_name')

    class Meta:
        model = models.FileFormat
        fields = '__all__'


class FileSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    type = serializers.HyperlinkedRelatedField(many=False, view_name='fileformat-detail', read_only=True)

    class Meta:
        model = models.File
        fields = '__all__'
        depth = 1


class DataTableSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.DataTable
        fields = '__all__'
        # depth = 1


class StorageTypeSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.StorageType
        fields = '__all__'


class DataStoreSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.DataStore
        fields = '__all__'


class PhysicalDataTableSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.PhysicalDataTable
        fields = '__all__'


class DataTypeSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.DataType
        fields = '__all__'


class VariableSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Variable
        fields = '__all__'


class ValueSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Value
        fields = '__all__'
