# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from decouple import config


class DataFacilityIntegrationsConfig(AppConfig):
    name = 'data_facility_integrations'

    def ready(self):
        from django.conf import settings
        if settings.RDS_INTEGRATION:
            from data_facility_integrations import k8s_workspace_hooks

        if settings.WS_K8S_INTEGRATION:
            from data_facility_integrations import rds_hooks
        pass
        if 'ACTIVE' in settings.SNS_HOOK and settings.SNS_HOOK['ACTIVE']:
            from data_facility_integrations import event_hooks
