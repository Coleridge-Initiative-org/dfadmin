from data_facility_admin.models import Project, ProjectMember, ProjectRole, User, ProjectTool
from django.core.signals import request_finished
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
import logging
from . import rds_client
from decouple import config
from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_K8S_CONFIG = {
    'REMOTE_DESKTOP_CPU':  config('K8S_REMOTE_DESKTOP_CPU', default=1),
    'REMOTE_DESKTOP_MEMORY':  config('K8S_REMOTE_DESKTOP_MEMORY', default=1000),
    'JUPYTER_CPU':  config('K8S_JUPYTER_CPU', default=1),
    'JUPYTER_MEMORY':  config('K8S_JUPYTER_MEMORY', default=1000),
    'JUPYTER_IMAGE':  config('WS_K8S_JUPYTER_IMAGE', default='?'),
    'REMOTE_DESKTOP_IMAGE':  config('WS_K8S_REMOTE_DESKTOP_IMAGE', default='?'),
}
logger.info('Loading K8S Hooks...')


@receiver(post_save, sender=Project)
def prepare_default_config_workspace_k8s(sender, instance, **kwargs):
    K8S = ProjectTool.TOOL_CHOICES.Workspace_K8s
    logger.debug('called prepare_default_config_workspace_k8s - from "{0}" with params: {1}'.format(sender, kwargs))
    project = instance
    try:
        k8s_config = ProjectTool.objects.get(project=project, tool_name=K8S)
        if not k8s_config.system_info:
            logger.info('Initialized the default config for K8S')
            k8s_config.system_info = DEFAULT_K8S_CONFIG
            k8s_config.save()
        else:
            logger.debug('Project %s already configured' % project)

    except ProjectTool.DoesNotExist:
        ProjectTool.objects.create(project=project, tool_name=K8S, system_info=DEFAULT_K8S_CONFIG)
        logger.info("Created new K8S config for project %s" % project.ldap_name)

    except Exception as ex:
        logger.error('Error on prepare_default_config_workspace_k8s for project %s' % project)
        logger.exception(ex)

    # logger.debug("prepare_default_config_workspace_k8s - END")
