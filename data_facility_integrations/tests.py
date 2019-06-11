# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .rds_hooks import *
import rds_client
from django.test import TestCase
from data_facility_admin.factories import ProjectFactory
from django.test import tag
import requests

from django.contrib.auth.models import User

class JwtAuth(TestCase):

    def setUp(self):
        User.objects.create_superuser(username='daniel', password='secret', email='', is_staff=True)

    @tag('integration')
    def test_check_if_can_read_token(self):
        ACCESS_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ1M0JmcDhSOTVJb0M0Q1pvenpuT2pQZjU5aF9kTm1mX3o4cVlkTkJvSjQ0In0.eyJqdGkiOiJjYTQ1YWZiYi05YWE5LTQzMDktYWRkNC0xNmYxZWZjOGM1MDYiLCJleHAiOjE1NTkyMzMzNzksIm5iZiI6MCwiaWF0IjoxNTU5MjMzMDc5LCJpc3MiOiJodHRwczovL2lkLmFkcmYuaW5mby9hdXRoL3JlYWxtcy9BRFJGIiwiYXVkIjpbImRmYWRtaW4iLCJhY2NvdW50Il0sInN1YiI6IjQ1ZDc3ZWRhLWMwZTItNDVmMS1iZmMyLWNmN2YyM2MwMWE1NyIsInR5cCI6IkJlYXJlciIsImF6cCI6ImRmYWRtaW4iLCJhdXRoX3RpbWUiOjAsInNlc3Npb25fc3RhdGUiOiJlOWRjYjc2My05ZWE4LTRmMWMtODE4ZS0yNDExYzU3YjI2YmUiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHBzOi8vZGZhZG1pbi5hZHJmLmluZm8iXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6InByb2ZpbGUgZW1haWwgRGZBZG1pbl9TY29wZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IkRhbmllbCBDYXN0ZWxsYW5pIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiZGFuaWVsIiwiZ2l2ZW5fbmFtZSI6IkRhbmllbCIsImZhbWlseV9uYW1lIjoiQ2FzdGVsbGFuaSIsImVtYWlsIjoiZGFuaWVsLmNhc3RlbGxhbmlAbnl1LmVkdSJ9.UgjoHvYv7f1Qm7rSvD4XvN5bfp4XsyHejErlnlWra-naNssiOtqVH6W-lThaz7KHG2YgorazIlrh0pq1WhKyqi1vA-bR5OanQ4MWrpxcmR7Crx_GneDTAuN29W3fCivaORxPvFMpc-Wgj05wR-RNjZS8Rh_Db_pkuRlGAD-27fWanYLoVU_W25esM2Yj-Uee8Y9fMlXkmJyvbMOffvlqgcUjBwtrm5vavk3MzsE0QG7Kb0ezq89vx9Z50gCbN5qmj9C3ZGY4XptTMIJmLkF7QcXLqyJuFt3fkpHNY4AihJMmFKhEU9HQZlQQ0DqsMlnuowbcZoaAP-FXAfQBb3YJ1g'

        url = "http://localhost:8000/api/v1/projects"

        querystring = {"member": "rafael", "fields": "name,tools"}

        headers = {
            'Authorization': "Bearer %s" % ACCESS_TOKEN,
            'User-Agent': "PostmanRuntime/7.13.0",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Postman-Token': "001eb74c-572b-495c-9e29-08c24026bc82,2adecb17-0c3a-4d13-89bc-2a32df717cc7",
            'accept-encoding': "gzip, deflate",
            'referer': "https://dfadmin.adrf.info/api/v1/projects?member=rafael&fields=name,tools",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        # print('<response>\n%s \n</response>' % response.text)

        self.assertTrue('Could not deserialize key data' not in response.text)


class TestRDSClient(TestCase):

    def setUp(self):
        self.test_project = ProjectFactory.create(name='dfadmin_test_project')
        self.test_project_tool = ProjectTool(project=self.test_project, tool_name=ProjectTool.TOOL_CHOICES.PG_RDS)

    @tag('integration')
    def test_rds_client_create_config_if_not_present(self):
        rds_client.init_system_info(self.test_project_tool)

        self.assertIsNotNone(self.test_project_tool.system_info)
        self.assertTrue(self.test_project_tool.system_info, 'System info is still None or empty.')

    # def test_rds_client_create_database(self):
    #     response = rds_client.create_database(self.test_project_tool)