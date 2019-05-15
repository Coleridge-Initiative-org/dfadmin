from data_facility_admin.models import Project, ProjectMember, ProjectRole, User, ProjectTool, Dataset
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
import logging
import boto3
# import boto3.ClientError
import json
from django.conf import settings

logger = logging.getLogger(__name__)

SNS_HOOK = settings.SNS_HOOK


def send_sns_event(topic, subject, payload):
    if SNS_HOOK['AWS_ACCESS_KEY_ID']:
        sns = boto3.client('sns',
                           region_name=SNS_HOOK['REGION'],
                           aws_access_key_id=SNS_HOOK['AWS_ACCESS_KEY_ID'],
                           aws_secret_access_key=SNS_HOOK['AWS_ACCESS_KEY']
                           )
    else:
        # When running on AWS, instance roles should be used.
        sns = boto3.client('sns', region_name=SNS_HOOK['REGION'])

    # try:
    payload["default"] = json.dumps(payload)

    response = sns.publish(
        TargetArn='%s:%s' % (SNS_HOOK['BASE_ARN'], topic),
        Subject=subject,
        Message=json.dumps(payload),
        MessageStructure='json'
    )

    # response = sns.publish(
    #     TopicArn='arn:aws:sns:us-east-1:441870321480:adrf-dataset-created',
    #     Message='Hello World!',
    # )

    print(response)
    logger.debug('SNS Response: %s' % response)
    # except ClientError as error:
    #     raise


@receiver(post_save, sender=Dataset)
def dataset_saved(sender, instance, **kwargs):
    logger.debug('Dataset saved - from "{0}" with instance: {1} params: {2}'.format(sender, instance, kwargs))

    # When added to an active project
    if kwargs['created']:
        topic = 'adrf-dataset-created'
        subject = 'Dataset created: {0}'.format(instance.dataset_id)
    else:
        topic = 'adrf-dataset-updated'
        subject = 'Dataset updated: {0}'.format(instance.dataset_id)

    payload = {
        'dataset_id': instance.dataset_id,
        'endpoint': 'dfadmin.dev.adrf.cloud/api/v1/datasets/{0}'.format(instance.dataset_id),
        'sender': 'DFAdmin',
        'status': instance.status,
        'name': instance.name,

    }

    # TODO: Log some nice message
    logger.info('Event generated: %s' % payload)
    # Write to SNS
    send_sns_event(topic, subject, payload)


# @receiver(post_delete, sender=ProjectTool)
# def project_tool_deleted(sender, instance, **kwargs):
#     logger.debug('project_tool_deleted - from "{0}" with params: {1}'.format(sender, kwargs))
#     project_tool = instance
#     project = project_tool.project
#     if project_tool.tool_name == ProjectTool.TOOL_CHOICES.PG_RDS:
#         logger.debug("RDS found")
#         rds_client.delete_database(project_tool)
#
