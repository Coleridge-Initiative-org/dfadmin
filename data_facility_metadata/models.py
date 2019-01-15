# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords
from django.core.exceptions import ValidationError

# Create your models here.
from data_facility_admin.models import Dataset
from model_utils import Choices

CHAR_FIELD_MAX_LENGTH = settings.CHAR_FIELD_MAX_LENGTH
TEXT_FIELD_MAX_LENGTH = settings.TEXT_FIELD_MAX_LENGTH


class FileFormat(models.Model):
    ''' Profile tags are used to describe users, such as tech-savy/non-tech-savy, CS-backgrund, etc.
        This should facilitate and improve communication with users.
    '''
    name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH)
    mimetype = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, unique=True)
    description = models.TextField( blank=True, null=True)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return  self.name

    class Meta:
        ordering = ['name']


class File(models.Model):
    ''' File represents a file that is part of a dataset.
    '''
    name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH)
    type = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, unique=True, blank=True, null=True)
    location = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, unique=True, blank=True, null=True)
    size = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True, null=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    format = models.ForeignKey(FileFormat, on_delete=models.CASCADE, blank=True, null=True)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        unique_together = ('dataset', 'name',)


class DataTable(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, blank=True, null=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)

    name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH)
    rows = models.IntegerField(blank=True, null=True)
    columns = models.IntegerField(blank=True, null=True)
    values = models.IntegerField(blank=True, null=True)
    gps_latitude_min = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=5)
    gps_latitude_max = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=5)
    gps_longitude_min = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=5)
    gps_longitude_max = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=5)
    size = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True)
    temporal_coverage_start = models.DateTimeField(blank=True, null=True)
    temporal_coverage_end = models.DateTimeField(blank=True, null=True)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    # @property
    # def dataset_id(self):
    #     return self.dataset.dataset_id

    def values_missing(self):
        return self.rows * self.columns - self.values

    def missing_percent(self):
        return self.values_missing() / self.rows * self.columns * 100

    def clean(self):
        # The logical table should relate only to files from the same dataset
        if self.file and self.file.dataset.id != self.dataset.id:
            raise ValidationError('The logical table should relate only to files from the same dataset. '
                                  'File dataset is "%s", which is different from "%s".' %
                                  (self.file.dataset, self.dataset))

    def physical_location(self):
        if self.data_store:
            return self.data_store.uri()
        else:
            return None

    def __str__(self):
        if self.file:
            return  self.name + ':' + self.file.name
        return  self.name

    class Meta:
        ordering = ['name', 'file']
        unique_together = ('dataset', 'name',)


class StorageType(models.Model):
    """
    This Entity represents the type of storage backend, such as S3, PG or Hive.
    """
    SCHEME_HELP_TEXT = "This field represent the storage type to be used (e.g. S3 or PG)"

    name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, help_text=SCHEME_HELP_TEXT, unique=True)
    description = models.TextField( help_text=SCHEME_HELP_TEXT,
                                   blank=True, null=True)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        my_string = self.name
        if self.description:
            my_string += ' (' + self.description + ')'
        return my_string

    class Meta:
        ordering = ['name']


class DataStore(models.Model):
    """
    Represents a physical (or logical) location in which we store the actual data. It can be a S3 bucket to store files
    or a database instance to store the tabular data.
    """
    type = models.ForeignKey(StorageType, on_delete=models.CASCADE)

    name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, unique=True)
    description = models.TextField( blank=True, null=True)
    host = models.CharField(max_length=TEXT_FIELD_MAX_LENGTH, blank=True, null=True,
                            help_text='Host or endpoint to access this Data Store physical location.')
    port = models.CharField(max_length=TEXT_FIELD_MAX_LENGTH, blank=True, null=True)
    database = models.CharField(max_length=TEXT_FIELD_MAX_LENGTH, blank=True, null=True)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def uri(self):
        uri = '%s://%s' % (self.type.name, self.host)
        if self.port:
            uri += ':%s' % self.port
        if self.database:
            uri += '/%s' % self.database
        return uri

    def __str__(self):
        me = self.name
        if self.description:
            me += ' (' + self.description + ')'
        return me

    class Meta:
        ordering = ['name']


class PhysicalDataTable(models.Model):
    """Indicates the physical location of this resource and how and where to access it.
    For further definitions and examples refer to - https://en.wikipedia.org/wiki/Uniform_Resource_Identifier
    """
    HOST_HELP_TEXT = "Indicates the physical address of the storage host for this resource"
    PATH_HELP_TEXT = "Indicates the path of this resource inside the given storage location"
    PHYSICAL_LOCATION_HELP_TEXT = 'Address of the physical location of this table.'

    logical_data_table = models.ForeignKey(DataTable, on_delete=models.CASCADE)

    data_store = models.ForeignKey(DataStore, on_delete=models.CASCADE,
                                   help_text=PHYSICAL_LOCATION_HELP_TEXT)
    # address = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, help_text=HOST_HELP_TEXT)
    path = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, help_text=PATH_HELP_TEXT)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def uri(self):
        return '%s/%s' % (self.data_store.uri(), self.path)

    def __str__(self):
        return self.uri()

    class Meta:
        ordering = ['logical_data_table', 'path']


class DataType(models.Model):
    CATEGORY_CHOICES = Choices('String', 'Numeric', 'Date/Time', 'Misc')
    name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, unique=True)
    description = models.TextField( blank=True, null=True)
    category = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH,
                                choices=CATEGORY_CHOICES, default=CATEGORY_CHOICES.String)
    data_store = models.ForeignKey(StorageType, on_delete=models.CASCADE,
                                   help_text='Which data store this data type is related to, such as Hive or Postgres.')

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name',]


class Variable(models.Model):
    name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH)
    data_table = models.ForeignKey(DataTable, on_delete=models.CASCADE, )
    provided_type = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True, null=True)
    detected_type = models.ForeignKey(DataType, blank=True, null=True,
                                      on_delete=models.CASCADE, related_name='detected_type')
    # profiler_most_detected_type = models.ForeignKey(DataType, blank=True, null=True)

    description = models.TextField( blank=True, null=True)
    unique_values = models.IntegerField(blank=True, null=True)
    missing_values = models.IntegerField(blank=True, null=True)
    top_k = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True, null=True)

    # extras, depending on type:
    #     max
    #     min
    #     historgram
    #     top_k
    #     mean
    #     stf
    #     top_value
    #     freq_top_value

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['data_table', 'name']
        unique_together = ('data_table', 'name',)


class Value(models.Model):
    """
    Value description for categorical variables inpired on
    https://www.icpsr.umich.edu/icpsrweb/ICPSR/studies/35476/datasets/0001/variables/M01MARSTA?archive=icpsr
    """
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE)

    value = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH)
    label = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True, null=True)
    description = models.TextField( blank=True, null=True)
    frequency = models.PositiveIntegerField(blank=True, null=True)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        me = self.value
        if self.label:
            me += '(' + self.label + ')'
        return me

    class Meta:
        ordering = ['variable', 'value']
        unique_together = ('variable', 'value',)

