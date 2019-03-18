# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-06 00:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    def populate_slurgs(apps, schema_editor):
        DataProvider = apps.get_model('data_facility_admin', 'DataProvider')
        for dp in DataProvider.objects.all():
            dp.save()

    dependencies = [
        ('data_facility_admin', '0029_auto_20190303_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataprovider',
            name='slug',
            field=models.SlugField(max_length=256, null=True, unique=True),
        ),

        migrations.RunPython(populate_slurgs),
    ]