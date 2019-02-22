# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .rds_hooks import *
import rds_client
from django.test import TestCase
from data_facility_admin.factories import ProjectFactory
from django.test import tag

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