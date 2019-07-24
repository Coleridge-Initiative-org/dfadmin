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
    logger.debug('[send_sns_event] Topic:%s, Subject:%s\nPayload:%s' % (topic, subject, payload))
    if SNS_HOOK['AWS_ACCESS_KEY_ID']:
        sns = boto3.client('sns',
                           region_name=SNS_HOOK['REGION'],
                           aws_access_key_id=SNS_HOOK['AWS_ACCESS_KEY_ID'],
                           aws_secret_access_key=SNS_HOOK['AWS_ACCESS_KEY'],
                           aws_session_token=SNS_HOOK['AWS_SESSION_TOKEN']
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
    logger.debug('SNS Response: %s' % response)
    # except ClientError as error:
    #     raise
    logger.info('SNS Event pushed with success: %s - %s' % (topic, subject))


def dataset_saved(instance, **kwargs):
    if not SNS_HOOK['ACTIVE']: return
    from data_facility_admin.models import Dataset

    logger.debug('Dataset saved - instance: {0} params: {1}'.format(instance, kwargs))

    created = kwargs['created'] if 'created' in kwargs else instance.id is None
    # When added to an active project
    if created:
        topic = SNS_HOOK['TOPIC_DATASET_CREATED']
        subject = 'Dataset created: {0}'.format(instance.dataset_id)
    else:
        topic = SNS_HOOK['TOPIC_DATASET_UPDATED']
        subject = 'Dataset updated: {0}'.format(instance.dataset_id)

    payload = {
        'entity_id': instance.dataset_id,
        'url': settings.DFADMIN_URL + '/api/v1/datasets/{0}'.format(instance.dataset_id),
        'sender': 'DFAdmin',
        'status': instance.status,
        'entity': instance.name,
    }
    send_sns_event(topic, subject, payload)

    # Check event dataset activated
    old_instance = Dataset.objects.get(id=instance.id)
    if instance.status == Dataset.STATUS_ACTIVE and (created or old_instance.status != instance.status):
            logger.debug('Dataset activated: %s' % instance.dataset_id)
            topic = SNS_HOOK['TOPIC_DATASET_ACTIVATED']
            subject = 'Dataset activated: {0}'.format(instance.dataset_id)
            send_sns_event(topic, subject, payload)

    # Check for deactivation
    if not created and instance.status != Dataset.STATUS_ACTIVE and old_instance.status == Dataset.STATUS_ACTIVE:
        logger.debug('Dataset activated: %s' % instance.dataset_id)
        topic = SNS_HOOK['TOPIC_DATASET_DEACTIVATED']
        subject = 'Dataset deactivated: {0}'.format(instance.dataset_id)
        send_sns_event(topic, subject, payload)



