# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-28 23:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_facility_admin', '0015_auto_20181128_1753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='description',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='historicaldataset',
            name='description',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
    ]
