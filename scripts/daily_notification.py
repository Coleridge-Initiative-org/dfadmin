import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from data_facility_admin.models import User, Project, Dataset, DatasetAccess, DfRole, UserDfRole
import logging


def admin_emails():
    '''
    Get emails from admins on DFAdmin to receive the updates.
    :return:
    '''
    # return ['daniel.castellani@nyu.edu']
    admin_group = DfRole.objects.get(ldap_name=settings.ADRF_ADMIN_GROUP)
    user_roles = UserDfRole.objects.filter(role=admin_group, begin__isnull=False)
    return [user_role.user.email for user_role in user_roles if user_role.active()
            and user_role.user.status in User.MEMBERSHIP_STATUS_WHITELIST]


def run(*args):
    logger = logging.getLogger(__name__)
    date = update_period(args)

    updates = get_system_updates(date)

    if any_updates(updates):
        email_subject = "DfAdmin Daily Notification"
        email_from = settings.EMAIL_FROM
        msg_plain = create_email_text(updates)

        print(msg_plain)
        print ('emails: ', admin_emails())

        msg = EmailMultiAlternatives(email_subject, msg_plain, email_from, admin_emails())

        msg.send()
        logger.debug('Sent email (%s)'
                     '\n Subject: '
                     '\n To:'
                     '\nText:' % (date, email_subject, admin_emails(), msg_plain, ))
    else:
        logger.debug('No updates to send today (%s)' % date)


def any_updates(updates):
    '''
    Checks if there are updates to be reported.
    :param updates: updates to report
    :return: True if updates should be reported
    '''
    for v in updates.itervalues():
        if len(v) > 0:
            return True
    return False


def update_period(args):
    '''
    Defines the update period being the last day or uses the date passed on the args.
    :param args:
    :return: date
    '''
    # try:
    #     date = datetime.datetime.strptime(args[0], "%Y-%m-%d").date()
    # except Exception as e:
    date = timezone.localtime(timezone.now()) - datetime.timedelta(days=1)
    return date


def create_email_text(updates):
    '''
    Prepare the email to be sent based on updates.
    :param updates: system updates to be considered.
    :return: email text
    '''
    data = {
        'users_created': updates['users_created'],
        'users_updated': updates['users_updated'],
        # 'users_enabled': updates['users_enabled'],
        # 'users_disabled': updates['users_disabled'],
        'users_pwd_expired': updates['users_pwd_expired'],
        'projects_created': updates['projects_created'],
        'projects_updated': updates['projects_updated'],
        'datasets_created': updates['datasets_created'],
        'datasets_updated': updates['datasets_updated'],
        'datasets_accesses_created': updates['access_created'],
        'datasets_accesses_updated': updates['access_updated'],
        'curr_date': datetime.date.today()
    }
    msg_plain = render_to_string('mail/daily_notification.txt', data)
    return msg_plain


def get_system_updates(given_date):
    '''
    Generat the system updates to send.
    :param given_date: desired date to get updates from.
    :return: system updates
    '''
    updated_filter = Q(updated_at__year=given_date.year,
                       updated_at__month=given_date.month,
                       updated_at__day=given_date.day,
                       # created_at__lt=given_date
                       )
    created_filter = Q(created_at__year=given_date.year,
                       created_at__month=given_date.month,
                       created_at__day=given_date.day)

    users_created = [str(user) for user in User.objects.filter(created_filter)]
    users_updated = User.objects.filter(updated_filter)
    users_updated_list = [str(user) for user in users_updated]
    users_pwd_expired = [str(u) for u in users_updated
                            if u.ldap_last_pwd_change is not None and
                                u.ldap_last_pwd_change.date() <= (timezone.now() - datetime.timedelta(days=60)).date()
                                and not u.system_user]

    projects_created = [str(project) for project in Project.objects.filter(created_filter)]
    projects_updated = [str(project) for project in Project.objects.filter(updated_filter)]

    datasets_created = [str(dataset) for dataset in Dataset.objects.filter(created_filter)]
    datasets_updated = [str(dataset) for dataset in Dataset.objects.filter(updated_filter)]

    access_created = [str(access) for access in DatasetAccess.objects.filter(created_filter)]
    access_updated = [str(access) for access in DatasetAccess.objects.filter(updated_filter)]

    updates = {
        'access_created': access_created,
        'access_updated': access_updated,
        'datasets_created': datasets_created,
        'datasets_updated': datasets_updated,
        'projects_created': projects_created,
        'projects_updated': projects_updated,
        'users_created': users_created,
        'users_pwd_expired': users_pwd_expired,
        'users_updated': users_updated_list,
    }
    return updates

