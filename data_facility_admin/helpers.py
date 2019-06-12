import ldap
import logging
from copy import deepcopy
import pytz
import random

from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.conf import settings
from data_facility_admin.keycloak import KeycloakAPI
from data_facility_admin.models import User, Dataset
from data_facility_admin.models import DfRole
from data_facility_admin.models import Project
from data_facility_admin.serializers import UserLDAPSerializer, DatasetLDAPSerializer
from data_facility_admin.serializers import ProjectLDAPSerializer
from data_facility_admin.serializers import DfRoleLDAPSerializer
from data_facility_admin.serializers import UserPrivateGroupLDAPSerializer
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
import datetime

class UserHelper:
    @staticmethod
    def pwgen(z, t):
        # EMPTY SET OF CHARACTERS
        charsset = ''
        # UPPERCASE -"O"
        U = 'ABCDEFGHIJKLMNPQRSTUVWXYZ'
        # lowercase -"l"
        L = 'abcdefghijkmnopqrstuvwxyz'
        N = '0123456789'
        S = '!@#$%^&*?<>'

        charssets = dict()

        # make sure we're using an integer, not a char/string
        z = int(z)
        for type in t:
            if 'u' in t:
                charssets['u'] = U
            if 'l' in t:
                charssets['l'] = L
            if 'n' in t:
                charssets['n'] = N
            if 's' in t:
                charssets['s'] = S

        return ''.join(random.choice(charssets[t[_ % len(t)]]) for _ in range(0, int(z)))

class KeycloakHelper(object):
    def __init__(self):
        self.api = KeycloakAPI(settings.KEYCLOAK['API_URL'], settings.KEYCLOAK['REALM'],
                               settings.KEYCLOAK['ADMIN_USERNAME'],
                               settings.KEYCLOAK['ADMIN_PASSWORD'])
        self.logger = logging.getLogger(__name__)

    def close(self):
        pass

    def send_welcome_email(self, df_users, reset_otp=False):
        self.api.ldap_full_sync(settings.KEYCLOAK['LDAP_ID'])
        for user in df_users:
            tmp_password = None
            # Reset user password on Keycloak
            try:
                keycloak_user = self.api.get_keycloak_user(user.email)
                keycloak_user = keycloak_user[0]
                tmp_password = UserHelper.pwgen(12, ['u', 'l', 'n', 's'])
                self.api.reset_user_password(keycloak_user['id'], tmp_password, True)
                keycloak_user["requiredActions"] = ["UPDATE_PASSWORD"]
                if reset_otp:
                    keycloak_user["requiredActions"].append("CONFIGURE_TOTP")
                self.api.update_keycloak_user(keycloak_user['id'], keycloak_user)
            except Exception as ex:
                self.logger.exception("Error reseting user password for user %s. Error message: %s"
                                      % (user.email, ex.message))
            # send welcome email
            try:
                msg_plain = render_to_string('mail/new_user.txt',
                                             {'username': user.username,
                                               'password': tmp_password,
                                               'current_time': timezone.now(),
                                               'keycloak_url': settings.WELCOME_EMAIL_KEYCLOAK_URL,
                                              'otp_instructions': settings.ADRF_MFA_ACTIVATED,
                                              'system_name': settings.ADRF_SYSTEM_NAME,
                                              })
                send_mail('Instructions for setting up Applied Data Analytics Program account',
                                    msg_plain,
                                    settings.EMAIL_FROM,
                                    [user.email])
            except Exception as ex:
                self.logger.exception("Error sending welcome email to user %s. Error message: %s"
                                      % (user.email, ex.message))

    def disable_user(self, df_user):
        try:
            keycloak_user = self.api.get_keycloak_user(df_user.email)
            if len(keycloak_user) == 0:
                self.logger.info('Ignoring user not found on keycloak: %s' % df_user.username)
                return
            keycloak_user = keycloak_user[0]
            if keycloak_user["enabled"]:
                keycloak_user["enabled"] = False
                self.api.update_keycloak_user(keycloak_user['id'], keycloak_user)
        except Exception as ex:
            self.logger.exception("Error disabling user %s. Error message: %s"
                                  % (df_user.email, ex.message))

    def enable_user(self, df_user):
        try:
            keycloak_user = self.api.get_keycloak_user(df_user.email)
            keycloak_user = keycloak_user[0]
            if not keycloak_user["enabled"]:
                keycloak_user["enabled"] = True
                self.api.update_keycloak_user(keycloak_user['id'], keycloak_user)
        except Exception as ex:
            self.logger.exception("Error enabling user %s. Error message: %s"
                                  % (df_user.email, ex.message))

class LDAPHelper:
    def init_ldap(self):
        self.__ldap_conn = ldap.initialize(settings.LDAP_SERVER)
        self.__ldap_conn.protocol_version = ldap.VERSION3
        self.__ldap_conn.simple_bind_s(settings.LDAP_SETTINGS['Connection']['BindDN'],
                                       settings.LDAP_SETTINGS['Connection']['BindPassword'])

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.init_ldap()

    def close(self):
        self.__ldap_conn.unbind()
        self.__ldap_conn = None

    @staticmethod
    def to_list_tuples(dict_):
        if dict_ is None:
            return None
        else:
            list_ = []
            for k, v in dict_.iteritems():
                list_.append((k, v))
            return list_

    def get_from_ldap(self, search_base, search_filter, values):
        if not search_base:
            base = settings.LDAP_BASE_DN
        else:
            base = "%s,%s" % (search_base, settings.LDAP_BASE_DN)
        result_data = self.__ldap_conn.search_s(base, ldap.SCOPE_SUBTREE, search_filter, values)
        return result_data

    def get_max_uid_number(self):
        search_filter = "(uid=*)"
        values = ['uidNumber']
        search_result = self.get_from_ldap(settings.LDAP_USER_SEARCH, search_filter, values)
        uid_numbers = [int(user[1]['uidNumber'][0]) for user in search_result if
                       'uidNumber' in user[1] and len(user[1]['uidNumber']) == 1]
        return max(uid_numbers)
    def get_max_gid_number(self):
        search_filter = "(cn=*)"
        values = ['gidNumber']
        search_result = self.get_from_ldap(None, search_filter, values)
        gid_numbers = [int(group[1]['gidNumber'][0]) for group in search_result if
                       'gidNumber' in group[1] and len(group[1]['gidNumber']) == 1]
        return max(gid_numbers)

    def get_ldap_projects(self):
        search_filter = "(&(objectclass=posixGroup)(|({0}=project-*)({0}=yproject-*)))" \
            .format(settings.PROJECT_LDAP_MAP['ldap_name'])
        values = settings.PROJECT_LDAP_MAP.values()
        return self.get_from_ldap(settings.LDAP_PROJECT_SEARCH, search_filter, values)

    @classmethod
    def flat_attributes_from_settings(cls, values):
        flat_values = []
        for value in values:
            if hasattr(value, '__iter__'):
                for v in value:
                    flat_values.append(v)
            else:
                flat_values.append(value)
        return flat_values

    def get_ldap_users(self):
        search_filter = "(%s=*)" % settings.USER_LDAP_MAP['username']
        # values = ['uid', 'mail', 'givenName', 'sn', ]
        values = self.flat_attributes_from_settings(settings.USER_LDAP_MAP.values())
        return self.get_from_ldap(settings.LDAP_USER_SEARCH, search_filter, values)

    def get_ldap_groups(self):
        search_filter = '(&(objectclass=posixGroup))'
        values = settings.PROJECT_LDAP_MAP.values()
        return self.get_from_ldap(settings.LDAP_GROUP_SEARCH, search_filter, values)

    def get_ldap_datasets(self):
        search_filter = '(&(objectclass=posixGroup))'
        values = settings.DATASET_LDAP_MAP.values()
        return self.get_from_ldap(settings.LDAP_DATASET_SEARCH, search_filter, values)

    def ldap_add(self, ldap_tuple):
        dn = ldap_tuple[0]
        if 'authTimestamp' in ldap_tuple[1]:
            ldap_tuple[1].pop("authTimestamp")
        if 'pwdChangedTime' in ldap_tuple[1]:
            ldap_tuple[1].pop("pwdChangedTime")
        # if 'posixAccount' in ldap_tuple[1]['objectClass']:
        #    ldap_tuple[1]['uidNumber'] = ["%s" % (self.get_max_uid_number() + 1)]
        # elif 'posixGroup' in ldap_tuple[1]['objectClass']:
        #    ldap_tuple[1]['gidNumber'] = ["%s" % (self.get_max_gid_number() + 1)]

        self.__ldap_conn.add_s(dn, self.to_list_tuples(ldap_tuple[1]))

    def ldap_update(self, ldap_tuple_new, ldap_tuple_curr):
        self.logger.debug("ldap_update() new=<{0}>, current=<{1}>".format(ldap_tuple_new, ldap_tuple_curr))

        dn = ldap_tuple_new[0]

        curr_attrs = set(ldap_tuple_curr[1].keys())
        new_attrs = set(ldap_tuple_new[1].keys())

        try:
            curr_attrs.remove("authTimestamp")
            new_attrs.remove("authTimestamp")
        except Exception as ex:
            self.logger.debug("There is no <authTimestamp> to remove for dn: %s" % dn)

        try:
            curr_attrs.remove("pwdChangedTime")
            new_attrs.remove("pwdChangedTime")
        except:
            self.logger.debug("There is no <pwdChangedTime> to remove for dn: %s" % dn)

        user_values = settings.USER_LDAP_MAP.values()
        user_flat_values = []
        for value in user_values:
            if hasattr(value, '__iter__'):
                for v in value:
                    user_flat_values.append(v)
            else:
                user_flat_values.append(value)
        user_attrs = set(user_flat_values)
        group_attrs = set(settings.GROUP_LDAP_MAP.values())
        project_attrs = set(settings.PROJECT_LDAP_MAP.values())
        user_private_group_attrs = set(settings.USER_PRIVATE_GROUP_LDAP_MAP.values())
        dataset_attrs = set(settings.DATASET_LDAP_MAP.values())

        updatable_attrs = user_attrs | group_attrs | project_attrs | user_private_group_attrs | dataset_attrs
        curr_attrs = curr_attrs & updatable_attrs
        new_attrs = new_attrs & updatable_attrs

        if 'AttributesBlackList' in settings.LDAP_SETTINGS['General'] and settings.LDAP_SETTINGS['General'][
            'AttributesBlackList']:
            blacklisted = set(settings.LDAP_SETTINGS['General']['AttributesBlackList'])
            blacklisted = blacklisted & curr_attrs
            for attr in blacklisted:
                for value in ldap_tuple_curr[1][attr]:
                    self.__ldap_conn.modify_s(dn, [(ldap.MOD_DELETE, attr, value)])

        for attr in curr_attrs - new_attrs:
            for value in ldap_tuple_curr[1][attr]:
                self.__ldap_conn.modify_s(dn, [(ldap.MOD_DELETE, attr, value)])
        for attr in new_attrs - curr_attrs:
            for value in ldap_tuple_new[1][attr]:
                self.__ldap_conn.modify_s(dn, [(ldap.MOD_ADD, attr, value)])
        for attr in new_attrs & curr_attrs:
            if len(ldap_tuple_curr[1][attr]) == 1 and len(ldap_tuple_new[1][attr]) == 1:
                if ldap_tuple_new[1][attr][0] != ldap_tuple_curr[1][attr][0]:
                    self.__ldap_conn.modify_s(dn, [(ldap.MOD_REPLACE, attr, ldap_tuple_new[1][attr][0])])
            else:
                for value in ldap_tuple_curr[1][attr]:
                    if value not in ldap_tuple_new[1][attr]:
                        self.__ldap_conn.modify_s(dn, [(ldap.MOD_DELETE, attr, value)])
                for value in ldap_tuple_new[1][attr]:
                    if value not in ldap_tuple_curr[1][attr]:
                        self.__ldap_conn.modify_s(dn, [(ldap.MOD_ADD, attr, value)])

    def import_users(self):
        self.logger.info("Starting partial import")
        ldap_users = self.get_ldap_users()
        self.logger.debug("Updating %d users from LDAP", len(ldap_users))
        for ldap_user in ldap_users:
            self.logger.debug("Updating user %s", ldap_user[0])
            df_user = None
            try:
                df_user = User.objects.filter(ldap_id=int(ldap_user[1]["uidNumber"][0])).first()
            except Exception:
                self.logger.info("The user %s is not in DFAdmin Database." % ldap_user[0])
            else:
                if not df_user:
                    self.logger.info("The user %s is not in DFAdmin Database." % ldap_user[0])
                else:
                    if settings.USER_LDAP_MAP["ldap_last_auth_time"] in ldap_user[1]:
                        try:
                            ldap_last_auth_time = ldap_user[1][settings.USER_LDAP_MAP["ldap_last_auth_time"]][0]
                            self.logger.debug("Updating last authentication time for user %s: %s", ldap_user[0], ldap_last_auth_time)
                            ldap_last_auth_time = datetime.datetime.strptime(ldap_last_auth_time, "%Y%m%d%H%M%SZ")
                            ldap_last_auth_time = ldap_last_auth_time.replace(tzinfo=pytz.utc)
                            if df_user.ldap_last_auth_time != ldap_last_auth_time:
                                df_user.ldap_last_auth_time = ldap_last_auth_time
                                df_user.changeReason = '[Import from LDAP] updated 302: ldap_last_auth_time'
                                df_user.save_without_historical_record()
                        except:
                            if df_user.ldap_last_auth_time is not None:
                                df_user.ldap_last_auth_time = None
                                df_user.changeReason = '[Import from LDAP] updated 307: ldap_last_auth_time (except)'
                                df_user.save_without_historical_record()
                    if settings.USER_LDAP_MAP["ldap_last_pwd_change"] in ldap_user[1]:
                        try:
                            ldap_last_pwd_change = ldap_user[1][settings.USER_LDAP_MAP["ldap_last_pwd_change"]][0]
                            self.logger.debug("Updating last password change time for user %s: %s", ldap_user[0], ldap_last_pwd_change)
                            ldap_last_pwd_change = datetime.datetime.strptime(ldap_last_pwd_change, "%Y%m%d%H%M%SZ")
                            ldap_last_pwd_change = ldap_last_pwd_change.replace(tzinfo=pytz.utc)
                            if df_user.ldap_last_pwd_change != ldap_last_pwd_change:
                                df_user.ldap_last_pwd_change = ldap_last_pwd_change
                                df_user.changeReason = '[Import from LDAP] updated ldap_last_pwd_change'
                                df_user.save()
                        except:
                            if df_user.ldap_last_pwd_change is not None:
                                df_user.ldap_last_pwd_change = None
                                df_user.changeReason = '[Import from LDAP] updated ldap_last_pwd_change (except)'
                                df_user.save()
                    if settings.USER_LDAP_MAP["ldap_lock_time"] in ldap_user[1]:
                        try:
                            ldap_lock_time = ldap_user[1][settings.USER_LDAP_MAP["ldap_lock_time"]][0]
                            self.logger.debug("Updating lock time for user %s: %s", ldap_user[0],
                                              ldap_lock_time)
                            ldap_lock_time = datetime.datetime.strptime(ldap_lock_time, "%Y%m%d%H%M%SZ")
                            ldap_lock_time = ldap_lock_time.replace(tzinfo=pytz.utc)
                            if df_user.ldap_lock_time != ldap_lock_time:
                                df_user.ldap_lock_time = ldap_lock_time
                                df_user.changeReason = '[Import from LDAP] updated ldap_lock_time'
                                df_user.save()
                        except:
                            if df_user.ldap_lock_time is not None:
                                df_user.ldap_lock_time = None
                                df_user.changeReason = '[Import from LDAP] updated ldap_lock_time (except)'
                                df_user.save()

    # # Locked in DFAdmin but not on LDAP anymore
    # df_user.status == User.STATUS_LOCKED_WRONG_PASSWD and settings.USER_LDAP_MAP["ldap_lock_time"] not in ldap_user[1]
    #
    # # Locked in DFAdmin and still has the flag on LDAP bc the user didn't login again.
    # df_user.status == User.STATUS_LOCKED_WRONG_PASSWD and timezone.now() > df_user.ldap_lock_time + datetime.timedelta(seconds=settings.LDAP_SETTINGS['General']['PpolicyLockDownDurationSeconds'])

                    if df_user.status == User.STATUS_LOCKED_WRONG_PASSWD and \
                        ( df_user.ldap_lock_time is None or
                        timezone.now() > df_user.ldap_lock_time + datetime.timedelta(seconds=settings.LDAP_SETTINGS['General']['PpolicyLockDownDurationSeconds']) ):
                        self.logger.info("User %s was unlocked automatically", ldap_user[0])
                        df_user.status = User.STATUS_ACTIVE
                        df_user.ldap_lock_time = None
                        df_user.changeReason = '[Import from LDAP] 344: Unlocking user (STATUS=STATUS_LOCKED_WRONG_PASSWD)'
                        df_user.save()
                    elif df_user.status == User.STATUS_ACTIVE and \
                        (df_user.ldap_lock_time is not None and timezone.now() > df_user.ldap_lock_time + datetime.timedelta(seconds=settings.LDAP_SETTINGS['General']['PpolicyLockDownDurationSeconds'])):
                        self.logger.info("User %s was unlocked automatically", ldap_user[0])
                        df_user.ldap_lock_time = None
                        df_user.changeReason = '[Import from LDAP] 344: Cleaning ldap_lock_time on DFadmin'
                        df_user.save()

                    elif df_user.status == User.STATUS_ACTIVE and \
                                    df_user.ldap_lock_time is not None and \
                                    timezone.now() < df_user.ldap_lock_time + datetime.timedelta(seconds=settings.LDAP_SETTINGS['General']['PpolicyLockDownDurationSeconds']):
                        df_user.status = User.STATUS_LOCKED_WRONG_PASSWD
                        df_user.changeReason = '[Import from LDAP] updated 350: STATUS_LOCKED_WRONG_PASSWD'
                        df_user.save()
                    self.logger.debug("User %s processed in import user", ldap_user[0])
        self.logger.info("Finishing LDAP partial import")

    def import_datasets(self):
        self.logger.info("Starting Datasets partial import")
        ldap_datasets = self.get_ldap_datasets()
        df_datasets = Dataset.objects.exclude(ldap_name__isnull=True)
        ldap_tuple_by_cn = dict(
            [(str(ldap_dataset[1][settings.DATASET_LDAP_MAP['ldap_name']][0]),
              ldap_dataset) for ldap_dataset in
             ldap_datasets])
        ldap_cns = set(
            [ldap_dataset[1][settings.DATASET_LDAP_MAP['ldap_name']][0] for ldap_dataset in
             ldap_datasets])
        df_dataset_cns = set([str(dataset.ldap_name) for dataset in df_datasets])

        cns_to_create = ldap_cns - df_dataset_cns
        self.logger.debug("Updating %d users from LDAP", len(cns_to_create))
        for ldap_dataset_cn in cns_to_create:
            ldap_dataset = ldap_tuple_by_cn[ldap_dataset_cn]
            self.logger.debug("Dataset %s being processed", ldap_dataset_cn)
            try:
                dataset_cn = ldap_dataset[1]['cn'][0].encode('ascii', 'ignore')
                ldap_id = ldap_dataset[1]['gidNumber'][0].encode('ascii', 'ignore')
                name = ldap_dataset[1][settings.DATASET_LDAP_MAP['ldap_name']][0]\
                    .encode('ascii', 'ignore')
            except:
                pass

            try:
                description = ldap_dataset[1][settings.DATASET_LDAP_MAP['description']][0]\
                    .encode('ascii', 'ignore')
            except:
                description = None

            # create
            try:
                dataset = Dataset(ldap_name=dataset_cn, ldap_id=ldap_id)
                dataset.description = description
                # doi <- name without 'dataset-'
                dataset.dataset_id = name.split(',')[0][8:]
                dataset.name = name.replace('-', ' ').title()
                dataset.ldap_id = ldap_id
                dataset.data_classification = Dataset.DATA_CLASSIFICATION_YELLOW
                dataset.save()
                self.logger.debug("Dataset %s has been created", ldap_dataset_cn)
            except:
                self.logger.exception("Dataset %s not created")
        self.logger.info("Finishing Datasets partial import")


    def export_users(self):
        #self.logger.info("Starting LDAP export")
        ldap_users = self.get_ldap_users()
        df_users = User.objects.all()
        #self.logger.debug("Exporting %d users", len(df_users))
        ldap_tuple_df = dict([(str(user.username), UserLDAPSerializer.dumps(user)) for user in df_users])
        ldap_tuple_curr = dict(
            [(ldap_user[1][settings.USER_LDAP_MAP['username']][0], ldap_user) for ldap_user in ldap_users])
        ldap_usernames = set([ldap_user[1][settings.USER_LDAP_MAP['username']][0] for ldap_user in ldap_users if
                              settings.USER_LDAP_MAP['username'] in ldap_user[1] and ldap_user[1][
                                  settings.USER_LDAP_MAP['username']]])
        df_usernames = set([df_user.username for df_user in df_users])
        users_just_in_ldap = ldap_usernames - df_usernames
        created_users = []

        keycloak_helper = KeycloakHelper()

        ldap_groups_tuple_curr = None
        ldap_private_group_tuple_new = None
        if settings.LDAP_SETTINGS['General']['UserPrivateGroups']:
            ldap_groups = self.get_ldap_groups()
            ldap_groups_tuple_curr = dict(
                [(str(ldap_group[1][settings.USER_PRIVATE_GROUP_LDAP_MAP['ldap_name']][0]), ldap_group) for ldap_group
                 in ldap_groups])
            ldap_private_group_tuple_new = dict(
                [(str(user.username), UserPrivateGroupLDAPSerializer.dumps(user)) for user in df_users])

        for username in users_just_in_ldap:
            if settings.LDAP_SETTINGS['General']['CleanNotInDB']:
                try:
                    self.__ldap_conn.delete_s(ldap_tuple_curr[username][0])
                    self.logger.warning("The user %s is not in DFAdmin Database and it's deleted." % username)
                except Exception:
                    self.logger.exception("User not deleted: %s" % username)
            else:
                self.logger.warning("The user %s is not in DFAdmin Database" % username)

        for df_user in df_users:
            if df_user.status == User.STATUS_NEW:
                try:
                    if settings.LDAP_SETTINGS['General']['UserPrivateGroups']:
                        try:
                            self.ldap_add(ldap_private_group_tuple_new[df_user.username])
                            self.logger.debug("Creating User Private Group %s" % df_user.username)
                        except Exception as ex:
                            self.logger.debug("Error creating User Private Group: " + ex.message)

                    self.ldap_add(ldap_tuple_df[df_user.username])
                    self.logger.debug("Creating user %s in LDAP" % df_user.username)
                    df_user.status = User.STATUS_ACTIVE
                    df_user.save()
                    created_users.append(df_user)
                    self.logger.debug("Set status of user %s to Active", df_user.username)
                except Exception:
                    self.logger.exception("The user %s was not created in LDAP" % df_user.username)
            elif df_user.status == User.STATUS_DISABLED or df_user.status == User.STATUS_LOCKED_BY_ADMIN:
                try:
                    ldap_tuple = ldap_tuple_df[df_user.username]
                    ldap_tuple[1][settings.USER_LDAP_MAP["ldap_lock_time"]] = ["000001010000Z"]
                    self.ldap_update(ldap_tuple, ldap_tuple_curr[df_user.username])
                    self.logger.debug("Locking user %s in LDAP" % df_user.username)
                    keycloak_helper.disable_user(df_user)
                except Exception:
                    self.logger.exception("The user %s was not disabled in LDAP" % df_user.username)
            elif df_user.status == User.STATUS_UNLOCKED_BY_ADMIN:
                try:
                    ldap_tuple = ldap_tuple_df[df_user.username]
                    if 'pwdAccountLockedTime' in ldap_tuple[1]:
                        ldap_tuple[1].pop(settings.USER_LDAP_MAP["ldap_lock_time"])
                    self.ldap_update(ldap_tuple, ldap_tuple_curr[df_user.username])
                    self.logger.debug("Unlocking user %s in LDAP" % df_user.username)
                    df_user.status = User.STATUS_ACTIVE
                    keycloak_helper.enable_user(df_user)
                    df_user.save()
                    self.logger.debug("Set status of user %s to Active", df_user.username)
                except Exception:
                    self.logger.exception("The user %s was not unlocked in LDAP" % df_user.username)
            elif df_user.status in User.MEMBERSHIP_STATUS_WHITELIST and \
                    (df_user.ldap_last_auth_time is not None and df_user.ldap_last_auth_time < timezone.now() -
                        datetime.timedelta(60, 0, 0)) or (df_user.ldap_last_auth_time is None and
                            df_user.created_at is not None and df_user.created_at < timezone.now() - datetime.timedelta(
                                60, 0, 0)):
                last_locked_time = df_user.history.filter(status=User.STATUS_LOCKED_INACTIVITY).first()
                last_unlocked_time = df_user.history.filter(status=User.STATUS_UNLOCKED_BY_ADMIN).first()
                if last_unlocked_time is not None and last_locked_time is not None \
                        and last_unlocked_time.history_date > last_locked_time.history_date and \
                                last_unlocked_time.history_date > timezone.now() - datetime.timedelta(60, 0, 0):
                    self.logger.debug("The user %s was not locked by inactivity because the user was unlocked by admin", df_user.username)
                else:
                    try:
                        ldap_tuple = ldap_tuple_df[df_user.username]
                        ldap_tuple[1][settings.USER_LDAP_MAP["ldap_lock_time"]] = ["000001010000Z"]
                        self.ldap_update(ldap_tuple, ldap_tuple_curr[df_user.username])
                        self.logger.debug("Locking the user %s in LDAP" % df_user.username)
                        df_user.status = User.STATUS_LOCKED_INACTIVITY
                        df_user.save()
                        self.logger.debug("Setting the status of user %s to Locked by Inactivity", df_user.username)
                    except Exception:
                        self.logger.exception("The user %s was not locked by inactivity in LDAP" % df_user.username)
            #Next is the update part, make sure the entry exists in LDAP before update ...
            elif df_user.username in ldap_tuple_curr:
                if settings.LDAP_SETTINGS['General']['UserPrivateGroups']:
                    if df_user.username in ldap_groups_tuple_curr:
                        try:
                            self.ldap_update(ldap_private_group_tuple_new[df_user.username],
                                             ldap_groups_tuple_curr[df_user.username])
                            self.logger.debug("Updating User Private Group for user %s", df_user.username)
                        except Exception:
                            self.logger.exception("UserPrivateGroup not updated: %s", df_user.username)
                    elif df_user.status in User.MEMBERSHIP_STATUS_WHITELIST:
                        try:
                            self.ldap_add(ldap_private_group_tuple_new[df_user.username])
                            self.logger.debug("Creating User Private Group for user %s in LDAP" % df_user.username)
                        except Exception:
                            self.logger.exception("UserPrivateGroup not created: %s", df_user.username)
                try:
                    self.ldap_update(ldap_tuple_df[df_user.username], ldap_tuple_curr[df_user.username])
                    self.logger.debug("Updating user %s in LDAP" % df_user.username)
                except Exception:
                    self.logger.exception("User not updated: %s" % df_user.username)

        keycloak_helper.send_welcome_email(created_users, reset_otp=True)

    def export_projects(self):
        self.logger.info("Starting projects export.")
        ldap_projects = self.get_ldap_projects()
        df_projects = Project.objects.exclude(ldap_name__isnull=True)
        ldap_tuple_new = dict([(str(proj.ldap_name).lower(), ProjectLDAPSerializer.dumps(proj)) for proj in df_projects])
        ldap_tuple_curr = dict(
            [(ldap_proj[1][settings.PROJECT_LDAP_MAP['ldap_name']][0].lower(), ldap_proj) for ldap_proj in ldap_projects])
        ldap_cns = set([ldap_proj[1][settings.PROJECT_LDAP_MAP['ldap_name']][0].lower() for ldap_proj in ldap_projects])
        df_proj_active = set([str(proj.ldap_name).lower() for proj in df_projects if proj.status == Project.STATUS_ACTIVE])
        df_proj_disabled = set([str(proj.ldap_name).lower() for proj in df_projects if proj.status != Project.STATUS_ACTIVE])

        cns_to_delete = df_proj_disabled & ldap_cns
        cns_to_create = df_proj_active - ldap_cns
        cns_to_update = df_proj_active & ldap_cns
        cns_just_in_ldap = ldap_cns - (df_proj_active | df_proj_disabled)

        for cn in cns_just_in_ldap:
            if settings.LDAP_SETTINGS['General']['CleanNotInDB']:
                try:
                    self.__ldap_conn.delete_s(ldap_tuple_curr[cn][0])
                    self.logger.debug("The project %s is not in DFAdmin Database and it's deleted." % cn)
                except Exception as e:
                    self.logger.exception("Project not deleted: %s" % cn)
            else:
                self.logger.warning("The project %s is not in DFAdmin Database" % cn)

        for cn in cns_to_delete:
            try:
                self.__ldap_conn.delete_s(ldap_tuple_curr[cn][0])
                self.logger.debug("The project %s has been deleted." % cn)
            except Exception as e:
                self.logger.exception("Project not deleted: %s" % cn)
        for cn in cns_to_create:
            try:
                self.ldap_add(ldap_tuple_new[cn])
                self.logger.debug("The project %s has been created." % cn)
            except Exception as e:
                self.logger.exception("Project not created: %s" % cn)
        for cn in cns_to_update:
            if settings.LDAP_SETTINGS['General']['RecreateGroups']:
                try:
                    self.__ldap_conn.delete_s(ldap_tuple_curr[cn][0])
                    orig_tuple = ldap_tuple_new[cn]
                    copy_tuple = deepcopy(orig_tuple)
                    if "member" in copy_tuple[1]:
                        copy_tuple[1].pop("member")
                    self.ldap_add(copy_tuple)
                    self.ldap_update(orig_tuple, copy_tuple)
                    self.logger.debug("The project %s has been recreadted." % cn)
                except Exception as e:
                    self.logger.exception("Project not recreated: %s" % cn)
            else:
                try:
                    self.ldap_update(ldap_tuple_new[cn], ldap_tuple_curr[cn])
                    self.logger.debug("The project %s has been updated" % cn)
                except Exception as e:
                    self.logger.exception("Project not updated: %s" % cn)
        self.logger.info("Project Export has ended.")

    def export_df_roles(self):
        self.logger.info("Starting DF Roles (LDAP Groups) Export.")
        ldap_groups = self.get_ldap_groups()
        df_roles = DfRole.objects.exclude(ldap_name__isnull=True)
        ldap_tuple_new = dict([(str(role.ldap_name), DfRoleLDAPSerializer.dumps(role)) for role in df_roles])
        ldap_tuple_curr = dict(
            [(ldap_group[1][settings.GROUP_LDAP_MAP['ldap_name']][0], ldap_group) for ldap_group in ldap_groups])
        ldap_cns = set([ldap_group[1][settings.GROUP_LDAP_MAP['ldap_name']][0] for ldap_group in ldap_groups])
        df_role_cns = set([str(role.ldap_name) for role in df_roles])

        cns_to_delete = ldap_cns - df_role_cns
        if settings.LDAP_SETTINGS['General']['UserPrivateGroups']:
            ldap_private_group_cns = set([str(user.username) for user in User.objects.all()])
            cns_to_delete = cns_to_delete - ldap_private_group_cns
        cns_to_create = df_role_cns - ldap_cns
        cns_to_update = df_role_cns & ldap_cns

        for cn in cns_to_delete:
            try:
                self.__ldap_conn.delete_s(ldap_tuple_curr[cn][0])
                self.logger.debug("DfRole %s has been deleted" % cn)
            except Exception as e:
                self.logger.exception("DfRole not deleted: %s" % cn)

        for cn in cns_to_create:
            try:
                self.ldap_add(ldap_tuple_new[cn])
                self.logger.debug("DfRole %s has been created", cn)
            except Exception as e:
                self.logger.exception("DfRole not created in LDAP: %s", cn)

        for cn in cns_to_update:
            if settings.LDAP_SETTINGS['General']['RecreateGroups']:
                try:
                    self.__ldap_conn.delete_s(ldap_tuple_curr[cn][0])
                    orig_tuple = ldap_tuple_new[cn]
                    copy_tuple = deepcopy(orig_tuple)
                    if "member" in copy_tuple[1]:
                        copy_tuple[1].pop("member")
                    self.ldap_add(copy_tuple)
                    self.ldap_update(orig_tuple, copy_tuple)
                    self.logger.debug("DfRole %s has been recreated", cn)
                except Exception as e:
                    self.logger.exception("DfRole not recreated: %s", cn)
            else:
                try:
                    self.ldap_update(ldap_tuple_new[cn], ldap_tuple_curr[cn])
                    self.logger.debug("DfRole %s has been updated", cn)
                except Exception as e:
                    self.logger.exception("DfRole not updated: %s", cn)
        self.logger.info("DF Roles (LDAP Groups) Export has ended.")

    def export_datasets(self):
        self.logger.info("Stating Datasets Export.")
        ldap_datasets = self.get_ldap_datasets()
        df_datasets = Dataset.objects.exclude(ldap_name__isnull=True)
        ldap_tuple_new = dict([(str(dataset.ldap_name), DatasetLDAPSerializer.dumps(dataset)) for dataset in df_datasets])
        ldap_tuple_curr = dict(
            [(ldap_dataset[1][settings.DATASET_LDAP_MAP['ldap_name']][0], ldap_dataset) for ldap_dataset in ldap_datasets])
        ldap_cns = set([ldap_dataset[1][settings.DATASET_LDAP_MAP['ldap_name']][0] for ldap_dataset in ldap_datasets])
        df_dataset_cns = set([str(dataset.ldap_name) for dataset in df_datasets])

        cns_to_delete = ldap_cns - df_dataset_cns

        cns_to_create = df_dataset_cns - ldap_cns
        cns_to_update = df_dataset_cns & ldap_cns

        # for cn in cns_to_delete:
        #     try:
        #         self.__ldap_conn.delete_s(ldap_tuple_curr[cn][0])
        #         self.logger.debug("Dataset %s has been deleted", cn)
        #     except Exception as e:
        #         self.logger.exception("Dataset not deleted: %s", cn)

        for cn in cns_to_create:
            try:
                self.ldap_add(ldap_tuple_new[cn])
                self.logger.debug("Dataset %s has been created", cn)
            except Exception as e:
                self.logger.exception("Dataset not created in LDAP: %s", cn)

        for cn in cns_to_update:
            if settings.LDAP_SETTINGS['General']['RecreateGroups']:
                try:
                    self.__ldap_conn.delete_s(ldap_tuple_curr[cn][0])
                    orig_tuple = ldap_tuple_new[cn]
                    copy_tuple = deepcopy(orig_tuple)
                    if "member" in copy_tuple[1]:
                        copy_tuple[1].pop("member")
                    self.ldap_add(copy_tuple)
                    self.ldap_update(orig_tuple, copy_tuple)
                    self.logger.debug("Dataset %s has been recreated", cn)
                except Exception as e:
                    self.logger.exception("Dataset not recreated: %s", cn)
            else:
                try:
                    self.ldap_update(ldap_tuple_new[cn], ldap_tuple_curr[cn])
                    self.logger.debug("Dataset %s has been updated", cn)
                except Exception as e:
                    self.logger.exception("Dataset not updated: %s", cn)
        self.logger.info("Datasets Export has ended.")

class EmailHelper:
    @staticmethod
    def send_updated_rules_of_behavior_email(users):
        logger = logging.getLogger(__name__)

        email_subject = "ADRF Rules of Behavior"
        email_from = settings.EMAIL_FROM

        email_text = render_to_string('mail/updated_rules_of_behavior.txt', {})
        logger.debug('Email message: \n%s' % email_text)

        if not users:
            user_emails = list(User.objects.filter(status__in=User.MEMBERSHIP_STATUS_WHITELIST,
                                                          system_user=False).values_list('email', flat=True))
        else:
            user_emails = (u.email for u in users)
        logger.debug('emails: ', user_emails)

        msg = EmailMultiAlternatives(email_subject, email_text, email_from, [], bcc=user_emails)

        msg.send()
        logger.info('Sent email (%s)\n Subject: %s\n To: %s\nText: %s' % (
            timezone.now(), email_subject, user_emails, email_text))

