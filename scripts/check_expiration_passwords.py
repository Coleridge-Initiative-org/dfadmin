#!/usr/bin/env python
import ldap, os
from datetime import datetime
from datetime import timedelta

# ----------------- DF Admin LDAP Configuration -------------------------
LDAP_BASE_DN = os.getenv('LDAP_BASE_DN', 'dc=adrf,dc=info')
LDAP_SERVER = os.getenv('LDAP_SERVER', "ldaps://meat.adrf.info")
LDAP_USER_SEARCH = os.getenv('LDAP_USER_SEARCH', "ou=People")
LDAP_GROUP_SEARCH = os.getenv('LDAP_GROUP_SEARCH', "ou=Groups")
LDAP_ADMIN_GROUP = os.getenv('LDAP_ADMIN_GROUP', "cn=adrf-admin-grp," + LDAP_GROUP_SEARCH)
LDAP_DATASET_SEARCH = os.getenv('LDAP_DATASET_SEARCH', "ou=Datasets")
LDAP_PROJECT_SEARCH = os.getenv('LDAP_PROJECT_SEARCH', "ou=Projects")
#
AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True

# --------------------------------- DF Admin LDAP import/export -----------------------
USER_LDAP_MAP = {
    "username": "uid",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
    "first_name%last_name": "cn",
    "ldap_id": ["uidNumber", "gidNumber"],
    "ldap_lock_time": "pwdAccountLockedTime",
    "ldap_last_auth_time": "authTimestamp",
    "ldap_ppolicy_configuration_dn": "pwdPolicySubentry"
}

LDAP_GROUP_FIELD_MEMBERS = os.getenv('LDAP_GROUP_FIELD_MEMBERS', "member")

PROJECT_LDAP_MAP = {
    "name": "name",
    "ldap_name": "cn",
    # "active_members+member|username": os.getenv('LDAP_PROJECT_FIELD_MEMBERS', "memberUid"),
    "active_members+ldap_full_dn": LDAP_GROUP_FIELD_MEMBERS,
    "abstract": "summary",
    "created_at": "creationdate",
    "ldap_id": "gidNumber",
}

LDAP_DATASET_FIELD_MEMBERS = os.getenv('LDAP_DATASET_FIELD_MEMBERS', "memberURL")

DATASET_LDAP_MAP = {
    "ldap_name": "cn",
    "active_members+ldap_full_dn": LDAP_GROUP_FIELD_MEMBERS,
    "ldap_id": "gidNumber",
}
GROUP_LDAP_MAP = {
    "ldap_name": "cn",
    # "active_users+user|username": os.getenv('LDAP_PROJECT_FIELD_MEMBERS', "memberUid"),
    "active_users+user|ldap_full_dn": LDAP_GROUP_FIELD_MEMBERS,
    "ldap_id": "gidNumber",
}

USER_PRIVATE_GROUP_LDAP_MAP = {
    "ldap_name": "cn",
    "ldap_id": "gidNumber",
}

LDAP_SETTINGS = {
    'Users': {
        'ObjectClasses': ['top', 'posixAccount', 'inetOrgPerson', 'adrfPerson', 'shadowAccount'],
        'DefaultHomeDirectory': '/nfshome/{0}',
        # 'DefaultGidNumber': '502',
        'DefaultLoginShell': '/bin/bash',
        'BaseDn': 'ou=People',
        'DefaultNDA': 'FALSE',
    },
    'Projects': {
        'ObjectClasses': ['top', 'adrfProject', 'posixGroup', 'groupOfMembers', 'group'],
        'BaseDn': 'ou=Projects',
    },
    'Datasets': {
#        'ObjectClasses': ['top', 'posixGroup', 'groupOfURLs'],
        'ObjectClasses': ['top', 'posixGroup', 'groupOfMembers', 'group'],
        'BaseDn': 'ou=Datasets',
    },
    'Groups': {
        'ObjectClasses': ['top', 'posixGroup', 'groupOfMembers', 'group'],
        'BaseDn': 'ou=Groups',
    },
    'UserPrivateGroups': {
        'ObjectClasses': ['top', 'posixGroup', 'groupOfMembers'],
    },
    'General': {
        'CleanNotInDB': False,
        'UserPrivateGroups': True,
        'AttributesBlackList': ['memberUid'],
        'RecreateGroups': False,
        'SystemUserPpolicyConfig': "cn=system-users,ou=policies,dc=adrf,dc=info"
    },
    'Connection': {
        'BindDN': os.getenv('LDAP_BIND_DN', "cn=admin,dc=adrf,dc=info"),
        'BindPassword': os.getenv('LDAP_BIND_PASSWD', "***REMOVED***"),
    }
}
__ldap_conn = ldap.initialize(LDAP_SERVER)
__ldap_conn.protocol_version = ldap.VERSION3
__ldap_conn.simple_bind_s(LDAP_SETTINGS['Connection']['BindDN'],
                                   LDAP_SETTINGS['Connection']['BindPassword'])


def get_ldap_users():
    search_filter = USER_LDAP_MAP['username'] + "=*"

    return get_from_ldap(LDAP_USER_SEARCH, search_filter, ['pwdChangedTime'])


def get_from_ldap(search_base, search_filter, values):
    if not search_base:
        base = LDAP_BASE_DN
    else:
        base = "%s,%s" % (search_base, LDAP_BASE_DN)
    result_data = __ldap_conn.search_s(base, ldap.SCOPE_SUBTREE, search_filter, values)
    return result_data

if __name__ == '__main__':
    print 'Start time:', datetime.now()
    print('\n\nInit...')

    resultado = get_ldap_users()

    for item in resultado:
        id_user = item[0]
        data = item[1]
        if data:
            datetime_object = datetime.strptime(data['pwdChangedTime'][0], "%Y%m%d%H%M%SZ")
            expire_date = datetime_object + timedelta(days=60)
            end_date = datetime.now() + timedelta(days=4)
            if expire_date < end_date:
                print('\n\nUser that needs to reset password:')
                print(id_user.split(',')[0])

                print('Expires in: ')
                print(expire_date)

    print('=== ============== ===')

#34.225.207.35   meat.adrf.info
