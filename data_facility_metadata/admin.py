# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from ajax_select.admin import AjaxSelectAdmin
from ajax_select import make_ajax_form
from simple_history.admin import SimpleHistoryAdmin
from .models import *
import nested_admin

# ------------------------ All inlines should come first. ------------------------


class PhysicalDataTableInline(admin.StackedInline):
    model = PhysicalDataTable
    extra = 0
    min_num = 0


class ValueInline(nested_admin.NestedTabularInline):
    model = Value
    extra = 0
    min_num = 0
    can_delete = False
    # show_change_link = True


class VariableInLine(nested_admin.NestedStackedInline):
    model = Variable
    extra = 0
    min_num = 0
    # show_change_link = True
    inlines = [ValueInline]

# ------------------------ Admins come after. ------------------------


@admin.register(FileFormat)
class FileAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'mimetype', 'description')
    search_fields = ('name', 'mimetype', 'description')


@admin.register(File)
class FileFormatAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'type', 'format')
    search_fields = ('name','type')
    list_filter = ['type', 'format']


@admin.register(DataTable)
class DataTableAdmin(SimpleHistoryAdmin, nested_admin.NestedModelAdmin):
    list_display = ('name', 'dataset', 'file', 'rows', 'columns', 'values',)
    search_fields = ['dataset__name', 'name', 'file__name']
    list_filter = ['dataset']
    inlines = [PhysicalDataTableInline, VariableInLine]


@admin.register(DataStore)
class DataStoreAdmin(SimpleHistoryAdmin):
    list_display = ['name', 'description', 'type', 'uri']
    search_fields = ['name', 'description']
    list_filter = ['type']


@admin.register(StorageType)
class StorageTypeAdmin(SimpleHistoryAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']


@admin.register(DataType)
class DataTypeAdmin(SimpleHistoryAdmin):
    list_display = ['name', ]#'category', 'description']
    # search_fields = ['name', 'description']
    # list_filter = ['data_store', 'category',]
