# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-30 03:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_facility_metadata', '0007_auto_20181129_2158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='name',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='historicalfile',
            name='name',
            field=models.CharField(max_length=256),
        ),
    ]
