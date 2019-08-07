from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def jwt_get_username_from_payload_handler(payload):
    logger.debug("jwt_get_username_from_payload_handler called with Payload=(%s)" % payload)
    if 'preferred_username' in payload:
        username = payload['preferred_username']
        logger.debug('API Called by JWT username: %s' % username)
        if 'email' in payload:
            email = payload['email']
        else:
            email = username+'@dfadmin.local'
        initialize_user_if_necessary(email, username)

        return payload['preferred_username']
    else:
        logger.error('Username not present on JWT API call')
        return None


def initialize_user_if_necessary(email, username):
    logger.debug("initialize_user_if_necessary(%s, %s)" % (email, username))
    from django.contrib.auth.models import Group, User

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User(username=username, is_active=True, email=email)
        user.save()
    try:
        logger.debug('Checking generic permission group: %s ' % settings.DFAFMIN_API_GENERIC_GROUP)
        generic_group = Group.objects.get(name=settings.DFAFMIN_API_GENERIC_GROUP)
        if not user.groups.filter(name=generic_group.name).exists():
            logger.info('User %s was not in group %s. Adding now... ' % (username, settings.DFAFMIN_API_GENERIC_GROUP))
            user.groups.add(generic_group)
            user.save()
            logger.info('User %s was not in group %s. User updated with success. ' % (
            username, settings.DFAFMIN_API_GENERIC_GROUP))
        else:
            logger.debug('User already has generic group.')

    except Group.DoesNotExist as ex:
        logger.error('The generic API permission group "%s" DoesNotExists.' % settings.DFAFMIN_API_GENERIC_GROUP)

    except Exception as ex:
        logger.error(
            'Error getting generic API permission group: %s. Probably this is a bad configuration.' % settings.DFAFMIN_API_GENERIC_GROUP,
            exc_info=True)

