# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-01-23 21:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_facility_admin', '0022_auto_20181217_2234'),
    ]

    operations = [
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AlterField(
            model_name='dataprovider',
            name='name',
            field=models.CharField(max_length=256, unique=True),
        ),
        migrations.AddField(
            model_name='dataset',
            name='keywords',
            field=models.ManyToManyField(blank=True, to='data_facility_admin.Keyword'),
        ),
    ]