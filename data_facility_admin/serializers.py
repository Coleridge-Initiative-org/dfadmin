''' Serializers for the ldap sync import/export scripts
'''
import datetime
from django.conf import settings
from data_facility_admin.models import User
import pytz

"""
The setting has the Maps that Serializer uses to create the ldap tuples from the Django Models.

When the key has a '+' sign, it means that the left side is a property or a method returning a list,
and the right side has the property the serializer should user for each object in the list.

When the key has a '%' sigh, it meand the Serializer will join the properties.

When the key has a '|', it means the Serializer has an object in the left side of the key and a
property in the right side of the key.
"""
def _get_attr_value(obj, attr_name):
    # TODO: Add docstring with description of language
    is_collection = False
    is_property = False
    is_multiple = False

    if '+' in attr_name:
        attr_name = attr_name.split('+')
        is_collection = True
    elif '|' in attr_name:
        attr_name = attr_name.split('|')
        is_property = True
    elif '%' in attr_name:
        attr_name = attr_name.split('%')
        is_multiple = True

    if len(attr_name) > 1 and is_multiple:
        return "%s %s" % (_get_attr_value(obj, attr_name[0]), _get_attr_value(obj, attr_name[1]))
    elif len(attr_name) > 1 and is_collection:
        try:
            collection = getattr(obj, attr_name[0]).all()
        except:
            try:
                collection = getattr(obj, attr_name[0])()
            except:
                return None
        return [_get_attr_value(e, attr_name[1]) for e in collection]
    elif len(attr_name) > 1 and is_property:
        return _get_attr_value(getattr(obj, attr_name[0]), attr_name[1])
    else:
        value = getattr(obj, attr_name)

        if isinstance(value, datetime.datetime):
            if value.tzinfo is not None:
                value = value.astimezone(pytz.utc)
            return value.strftime("%Y%m%d%H%M%SZ")
        else:
            final_value = None
            try:
                final_value = value()
            except:
                final_value = value

            if final_value is None:
                return None
            else:
                return str(final_value)
            


def _list_if_not(value):
    if value is None:
        return []
    elif hasattr(value, '__iter__'):
        return value
    return [value]


def _add_if_not_empty(dict_, key_, value_):
    if value_:
        dict_[key_] = value_


class UserLDAPSerializer(object):
    """
    LDAP Tuple example:

    ('uid=chiahsuanyang,ou=People,dc=adrf,dc=info',
        {
            'gidNumber': ['502'],
            'givenName': ['Chia-Hsuan'],
            'homeDirectory': ['/nfshome/chiahsuanyang'],
            'loginShell': ['/bin/bash'],
            'objectClass': ['inetOrgPerson','posixAccount','top', 'adrfPerson'],
            'uid': ['chiahsuanyang'],
            'uidNumber': ['1039'],
            'mail': ['cy1138@nyu.edu'],
            'sn': ['Yang'],
            'cn': ['Chia-Hsuan Yang'],
        }
    )
    """

    def __init__(self):
        pass

    @staticmethod
    def loads(ldap_tuple):
        user = User()
        try:
            user.ldap_name = ldap_tuple[1][settings.USER_LDAP_MAP['username']][0] \
                .encode('ascii', 'ignore')
        except:
            pass
        try:
            user.email = ldap_tuple[1][settings.USER_LDAP_MAP['email']][0].encode('ascii', 'ignore')
        except:
            pass
        try:
            user.first_name = ldap_tuple[1][settings.USER_LDAP_MAP['first_name']][0] \
                .encode('ascii', 'ignore')
        except:
            pass
        try:
            user.last_name = ldap_tuple[1][settings.USER_LDAP_MAP['last_name']][0] \
                .encode('ascii', 'ignore')
        except:
            pass
        return user

    @staticmethod
    def dumps(user):
        user_dn = str("uid=%s,%s,%s" % (user.username(), settings.LDAP_USER_SEARCH,
                                        settings.LDAP_BASE_DN))
        data = {
            'objectClass': settings.LDAP_SETTINGS['Users']['ObjectClasses'],
            # 'gidNumber': [settings.LDAP_SETTINGS['Users']['DefaultGidNumber']],
            # 'uidNumber': "%s" % get_max_uid_number() + 1),
            'loginShell': [settings.LDAP_SETTINGS['Users']['DefaultLoginShell']],
            'homeDirectory': [settings.LDAP_SETTINGS['Users']['DefaultHomeDirectory']
                                  .format(user.username())],
            'nda': [settings.LDAP_SETTINGS['Users']['DefaultNDA']],
        }
        for df_key, ldap_key in settings.USER_LDAP_MAP.iteritems():
            if df_key == "ldap_last_auth_time" or df_key == "ldap_last_pwd_change":
                continue
            if hasattr(ldap_key, '__iter__'):
                for key in ldap_key:
                    _add_if_not_empty(data, key, _list_if_not(_get_attr_value(user, df_key)))
            else:
                _add_if_not_empty(data, ldap_key, _list_if_not(_get_attr_value(user, df_key)))
        return user_dn, data


class ProjectLDAPSerializer(object):
    """LDAP Tuple example:

        ('cn=project-Food Analysis,ou=Projects,dc=adrf,dc=info',
            {
                'objectClass': ['posixGroup', 'groupOfMembers', 'adrfProject'],
                'summary': ['required field'],
                'name': ['Food Analysis'],
                'gidNumber': ['7003'],
                'creationdate': ['20161130221426Z'],
                'cn': ['project-Food Analysis'],
                'memberUid': ['rafael', 'will'],
            }
        )
    """

    def __init__(self):
        pass

    @staticmethod
    def loads(ldap_tuple):
        pass

    @staticmethod
    def dumps(project):
        dn = str("cn=%s,%s,%s" % (project.ldap_name, settings.LDAP_PROJECT_SEARCH,
                                  settings.LDAP_BASE_DN))

        data = {
            'objectClass': settings.LDAP_SETTINGS['Projects']['ObjectClasses'],
        }
        for df_key, ldap_key in settings.PROJECT_LDAP_MAP.iteritems():
            _add_if_not_empty(data, ldap_key, _list_if_not(_get_attr_value(project, df_key)))
        return dn, data


class DfRoleLDAPSerializer(object):
    """LDAP Tuple example:

        ('cn=annotation-reviewers,ou=Groups,dc=adrf,dc=info',
            {
                'objectClass': ['posixGroup', 'groupOfMembers'],
                'gidNumber': ['5004'],
                'cn': ['annotation-reviewers'],
                'memberUid': ['rafael', 'will'],
            }
        )
    """

    def __init__(self):
        pass

    @staticmethod
    def loads(ldap_tuple):
        pass

    @staticmethod
    def dumps(role):
        dn = str("cn=%s,%s,%s" % (role.ldap_name, settings.LDAP_GROUP_SEARCH, settings.LDAP_BASE_DN))
        data = {
            'objectClass': settings.LDAP_SETTINGS['Groups']['ObjectClasses'],
        }
        for df_key, ldap_key in settings.GROUP_LDAP_MAP.iteritems():
            _add_if_not_empty(data, ldap_key, _list_if_not(_get_attr_value(role, df_key)))
        return dn, data


class UserPrivateGroupLDAPSerializer(object):
    """LDAP Tuple example:

        ('cn=annotation-reviewers,ou=Groups,dc=adrf,dc=info',
            {
                'objectClass': ['posixGroup', 'top'],
                'gidNumber': ['5004'],
                'cn': ['annotation-reviewers'],
            }
        )
    """

    def __init__(self):
        pass

    @staticmethod
    def loads(ldap_tuple):
        pass

    @staticmethod
    def dumps(user):
        dn = str("cn=%s,%s,%s" % (user.username(), settings.LDAP_GROUP_SEARCH, settings.LDAP_BASE_DN))

        data = {
            'objectClass': settings.LDAP_SETTINGS['UserPrivateGroups']['ObjectClasses'],
        }
        for df_key, ldap_key in settings.USER_PRIVATE_GROUP_LDAP_MAP.iteritems():
            _add_if_not_empty(data, ldap_key, _list_if_not(_get_attr_value(user, df_key)))

        return dn, data


class DatasetLDAPSerializer(object):
    """LDAP Tuple example:

        ('cn=adrf-000001,ou=Datasets,dc=adrf,dc=info',
            {
                'objectClass': ['top', 'posixGroup', 'groupOfURLs'],
                'gidNumber': ['5004'],
                'cn': ['adrf-000001'],
            }
        )
    """

    def __init__(self):
        pass

    @staticmethod
    def loads(ldap_tuple):
        pass

    @staticmethod
    def dumps(dataset):
        dn = str("cn=%s,%s,%s" % (dataset.ldap_name, settings.LDAP_DATASET_SEARCH, settings.LDAP_BASE_DN))

        data = {
            'objectClass': settings.LDAP_SETTINGS['Datasets']['ObjectClasses'],
        }
        for df_key, ldap_key in settings.DATASET_LDAP_MAP.iteritems():
            _add_if_not_empty(data, ldap_key, _list_if_not(_get_attr_value(dataset, df_key)))

        return dn, data
