import logging

logger = logging.getLogger(__name__)


def jwt_get_username_from_payload_handler(payload):
    from django.contrib.auth.models import Group, User

    if 'preferred_username' in payload:
        username = payload['preferred_username']
        logger.debug('API Called by JWT username: %s' % username)
        if 'email' in payload:
            email = payload['email']
        else:
            email = username+'@dfadmin.local'
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username, is_active=True, email=email)
            user.save()

        # TODO: Add Groups

        return payload['preferred_username']
    else:
        logger.error('Username not present on JWT API call')
        return None

