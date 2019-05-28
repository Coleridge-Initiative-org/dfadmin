# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

import logging
logger = logging.getLogger(__name__)

class DataFacilityIntegrationsConfig(AppConfig):
    name = 'data_facility_integrations'

    def ready(self):
        from django.conf import settings
        logger.info('Loading integrations...')

        if settings.RDS_INTEGRATION:
            from data_facility_integrations import rds_hooks

        if settings.WS_K8S_INTEGRATION:
            from data_facility_integrations import k8s_workspace_hooks
            logger.info('WS_K8S_INTEGRATION Activated')

        if 'ACTIVE' in settings.SNS_HOOK and settings.SNS_HOOK['ACTIVE']:
            from data_facility_integrations import event_hooks
            logger.info('SNS_HOOK Activated')

        logger.info('DFAdmin integrations loaded.')
