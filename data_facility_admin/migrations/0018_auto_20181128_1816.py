# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-28 23:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_facility_admin', '0017_auto_20181128_1815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='dataset_citation',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicaldataset',
            name='dataset_citation',
            field=models.TextField(blank=True, null=True),
        ),
    ]
