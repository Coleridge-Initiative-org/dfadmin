from data_facility_admin.models import Project, ProjectMember, ProjectRole, User, ProjectTool
from django.core.signals import request_finished
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
import logging
from . import rds_client
from decouple import config

logger = logging.getLogger(__name__)

DEFAULT_K8S_CONFIG = {
    'REMOTE_DESKTOP_CPU':  config('RDS_DEFAULT_CONFIG__REGION', default=1),
    'REMOTE_DESKTOP_MEMORY':  config('RDS_DEFAULT_CONFIG__REGION', default=1000),
    'JUPYTER_CPU':  config('RDS_DEFAULT_CONFIG__REGION', default=1),
    'JUPYTER_MEMORY':  config('RDS_DEFAULT_CONFIG__REGION', default=1000),
}


@receiver(post_save, sender=Project)
def prepare_default_config_workspace_k8s(sender, instance, **kwargs):
    if not settings.WS_K8S_INTEGRATION: return

    K8S = ProjectTool.TOOL_CHOICES.Workspace_K8s
    logger.debug('called project_saved - from "{0}" with params: {1}'.format(sender, kwargs))
    project = instance
    try:
        k8s_config = ProjectTool.objects.get(project=project, tool_name=K8S)
        if not k8s_config.system_info:
            k8s_config.system_info = DEFAULT_K8S_CONFIG
    except ProjectTool.DoesNotExist:
        ProjectTool.objects.create(project=project, tool_name=K8S, system_info=DEFAULT_K8S_CONFIG)
        logger.info("Created new K8S config for project %s" % project.ldap_name)
    print("Project Default Config - END")
