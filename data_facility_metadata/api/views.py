""" This Module generates the Django views for this app. """

# from django.shortcuts import render

# Create your views here.

from rest_framework import mixins, generics, viewsets
from rest_framework.generics import ListAPIView
from data_facility_metadata.models import *
from . import serializers as serializers

# TODO: Add API versioning: https://www.django-rest-framework.org/api-guide/versioning/


class FileFormatViewSet(viewsets.ModelViewSet):
    queryset = FileFormat.objects.all()
    serializer_class = serializers.FileFormatSerializer
    filter_fields = '__all__'
    search_fields = '__all__'


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = serializers.FileSerializer
    filter_fields = '__all__'
    search_fields = '__all__'


class DataTableViewSet(viewsets.ModelViewSet):
    queryset = DataTable.objects.all()
    serializer_class = serializers.DataTableSerializer
    filter_fields = '__all__'
    search_fields = '__all__'


class StorageTypeViewSet(viewsets.ModelViewSet):
    queryset = StorageType.objects.all()
    serializer_class = serializers.StorageTypeSerializer
    filter_fields = '__all__'
    search_fields = '__all__'


class DataStoreViewSet(viewsets.ModelViewSet):
    queryset = DataStore.objects.all()
    serializer_class = serializers.DataStoreSerializer
    filter_fields = '__all__'
    search_fields = '__all__'


class PhysicalDataTableViewSet(viewsets.ModelViewSet):
    queryset = PhysicalDataTable.objects.all()
    serializer_class = serializers.PhysicalDataTableSerializer
    filter_fields = '__all__'
    search_fields = '__all__'


class DataTypeViewSet(viewsets.ModelViewSet):
    queryset = DataType.objects.all()
    serializer_class = serializers.DataTypeSerializer
    filter_fields = '__all__'
    search_fields = '__all__'


class VariableViewSet(viewsets.ModelViewSet):
    queryset = Variable.objects.all()
    serializer_class = serializers.VariableSerializer
    filter_fields = '__all__'
    search_fields = '__all__'


class ValueViewSet(viewsets.ModelViewSet):
    queryset = Value.objects.all()
    serializer_class = serializers.ValueSerializer
    filter_fields = '__all__'
    search_fields = '__all__'
