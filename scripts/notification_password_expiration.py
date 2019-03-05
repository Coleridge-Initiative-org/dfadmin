import datetime
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

from data_facility_admin.models import User, Project, Dataset, DatasetAccess

MAX_PWD_AGE = settings.ADRF_PASS_EXPIRATION_TIME
AGE_LIMIT = MAX_PWD_AGE - 7

EMAIL_SUBJECT = "Please update your ADRF password"

def run(*args):
    TODAY = timezone.now()
    near_expiration_date = timezone.now() - datetime.timedelta(days=AGE_LIMIT)

    print('Notification of Password Expiration on '
          + near_expiration_date.strftime("%Y-%m-%d %H:%M:%S"))

    # 1. get all active users that the password is to expire in at least 7 days
    users = User.objects.filter(status__in=User.MEMBERSHIP_STATUS_WHITELIST,
                                ldap_last_pwd_change__lte=near_expiration_date)

    if len(users) == 0:
        print(' No one to notify.')
        return

    emails = []
    for user in users:
        pwd_age = (timezone.now() - user.ldap_last_pwd_change).days
        remaining_days = MAX_PWD_AGE - pwd_age

        print(' Notifying {0} > {1}. Expires in {2} days.'.format(str(user),
                                                                      user.email,
                                                                      str(remaining_days)))

        data = {
            'remaining_days': remaining_days,
            'username': user.username,
            'instructions_link': settings.PWD_RESET_INSTRUCTIONS,
            'curr_date': TODAY,
            'url': settings.ADRF_URL,
        }
        msg_plain = render_to_string('mail/pwd_expiration_email.txt', data)

        # print(msg_plain)
        emails.append((EMAIL_SUBJECT, msg_plain, settings.EMAIL_FROM, [user.email]))

    send_mass_mail(emails)
