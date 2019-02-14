# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from decouple import config


class DataFacilityIntegrationsConfig(AppConfig):
    name = 'data_facility_integrations'

    def ready(self):
        if config('RDS_INTEGRATION', cast=bool, default=False):
            from data_facility_integrations import rds_hooks

        if config('WS_K8S_INTEGRATION', cast=bool, default=False):
            from data_facility_integrations import k8s_workspace_hooks
