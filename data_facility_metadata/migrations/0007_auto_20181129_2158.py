# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-30 02:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_facility_metadata', '0006_auto_20181128_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalvariable',
            name='provided_type',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='variable',
            name='provided_type',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
