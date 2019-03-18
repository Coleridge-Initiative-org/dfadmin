#!/usr/bin/env python
# From DjangoSnippets: https://djangosnippets.org/snippets/893/
import os

import ldap
import datetime
import pytz
from django.utils import timezone
from django.db.utils import IntegrityError

from django.conf import settings
from data_facility_admin.models import Project, User, ProjectMember, ProjectRole, DfRole, UserDfRole, DatasetAccess, Dataset, MISSING_INFO_FLAG

USER_ATTRIBUTES = {
    "username": "uid",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
    "ldap_id": "uidNumber",
    "ldap_lock_time": "pwdAccountLockedTime",
    "ldap_last_auth_time": "authTimestamp",
    "ldap_ppolicy_configuration_dn": "pwdPolicySubentry",
    "ldap_last_pwd_change": "pwdChangedTime"

}
PROJECT_ATTRIBUTES = {
    "name": "name",
    "ldap_name": "cn",
    "members": os.getenv('LDAP_PROJECT_FIELD_MEMBERS', "member"),
    "member_username": 'uid=',
    "description": "summary",
    "ldap_id":  "gidNumber",
}
GROUP_ATTRIBUTES = {
    "name": "cn",
    "members": os.getenv('LDAP_GROUP_FIELD_MEMBERS', "member"),
    "member_username": 'uid=',
    "ldap_id":  "gidNumber",
}
DATASET_ATTRIBUTES = settings.DATASET_LDAP_MAP

# AUTH_LDAP_BASE_PASS = os.environ.get('LDAP_SYNC_PASS')
AUTH_LDAP_SCOPE = ldap.SCOPE_SUBTREE
DEFAULT_PROJECT_ROLE = 'Member'
DEFAULT_DF_ROLE = 'Other/Missing'
TIME_NOW = timezone.now()
DEBUG = False

ERRORS = {}


def add_error(key, message=None):
    if key not in ERRORS:
        ERRORS[key] = 0
    ERRORS[key] += 1
    if message is None: message = key
    print '\033[31m   [Error] %s: %s \033[0m' % (key, message)


def get_from_ldap(search_base=None, search_filter=None, values=None):
    l = ldap.initialize(settings.LDAP_SERVER)
    l.protocol_version = ldap.VERSION3
    l.simple_bind_s()
    if search_base is None:
        search = settings.LDAP_BASE_DN
    else:
        search = search_base + ',' + settings.LDAP_BASE_DN
    if search_filter is None:
        search_filter = '*'
    result_id = l.search(search, AUTH_LDAP_SCOPE, search_filter, values)
    result_type, result_data = l.result(result_id, 1)
    l.unbind()
    return result_data


def get_members(ldap_members):
    members = []
    for m in ldap_members:
        # memberUid
        if 'uid=' in m:
            member = m.lstrip('uid=').split(',')[0]
        # memberURL
        elif 'sub?(cn=' in m:
            member = m.split('cn=')[1].rstrip(')')
        # member
        elif 'cn=' in m:
            member = m.lstrip('cn=').split(',')[0]
        else:
            member = m
        members.append(member.encode('ascii', 'ignore'))
    # print('members=', members)
    return members


def get_ldap_projects():
    search_filter = "(&(objectclass=posixGroup)(|({0}=project-*)({0}=yproject-*)))" \
        .format(PROJECT_ATTRIBUTES['name'])
    values = PROJECT_ATTRIBUTES.values()
    return get_from_ldap(settings.LDAP_PROJECT_SEARCH, search_filter, values)


def get_ldap_users():
    search_filter = USER_ATTRIBUTES['username'] + "=*"
    values = USER_ATTRIBUTES.values()
    return get_from_ldap(settings.LDAP_USER_SEARCH, search_filter, values)


def get_ldap_groups():
    search_filter = '(&(objectclass=posixGroup))'
    values = GROUP_ATTRIBUTES.values()
    return get_from_ldap(settings.LDAP_GROUP_SEARCH, search_filter, values)


def get_ldap_datasets():
    search_filter = '(&(objectclass=posixGroup))'
    values = ['*'] #DATASET_ATTRIBUTES.values()
    return get_from_ldap(settings.LDAP_DATASET_SEARCH, search_filter, values)


def import_groups():
    ldap_groups = get_ldap_groups()

    try:
        default_role = DfRole.objects.get(name=DEFAULT_DF_ROLE)
    except DfRole.DoesNotExist:
        raise Exception('Default Role does not exists. Please create it before running the import script.')

    for group in ldap_groups:
        if DEBUG: print('ldap_group=', group)
        # get project name and ldap_group

        try:
            group_cn = group[1]['cn'][0].encode('ascii', 'ignore')
            ldap_id = group[1]['gidNumber'][0].encode('ascii', 'ignore')
            name = group[1][GROUP_ATTRIBUTES['name']][0].encode('ascii', 'ignore')
            if name == 'None': continue # TODO: Remove this line.
            # ignore project groups
            if name.startswith('project-') or name.startswith('yproject-'): continue
        except:
            add_error('Group without name', group)
            pass

        try:
            # Check if this group is a user group.
            User.objects.get(ldap_id=ldap_id)
            continue
        except User.DoesNotExist:
            pass

        print ' Processing group: %s' % name
        try:
            description = group[1][PROJECT_ATTRIBUTES['description']][0].encode('ascii', 'ignore')
        except:
            add_error('Group without description', group_cn)
            description = None

        # retrieve or create
        try:
            df_role = DfRole.objects.get(ldap_name=group_cn)
        except DfRole.DoesNotExist:
            df_role = DfRole(ldap_name=group_cn, ldap_id=ldap_id)

        df_role.description = description
        df_role.name = name.replace('-', ' ').title()
        df_role.ldap_id = ldap_id

        df_role.save()

        # Get members of groups
        if GROUP_ATTRIBUTES['members'] in group[1]:
            current_members = group[1][GROUP_ATTRIBUTES['members']]

            print '  Disabling old members:'
            for previous_member in df_role.userdfrole_set.all():
                if previous_member.active() and previous_member.user.username not in current_members:
                    previous_member.end = TIME_NOW
                    previous_member.save()
                    print '   > Member disabled:', previous_member.user

            print '  Adding/Updating current members:'
            for username in get_members(current_members):
                print '   > Member:', username
                try:
                    user = User.objects.get(ldap_name=username)
                except User.DoesNotExist:
                    add_error('Group member does not exists', username)
                    continue

                try:
                    user_role = UserDfRole.objects.get(role=df_role, user=user)
                except UserDfRole.DoesNotExist:
                    user_role = UserDfRole(role=df_role, user=user)
                    user_role.begin = TIME_NOW
                user_role.save()
        else:
            add_error('Group has no members', name)


def import_projects():
    ldap_projects = get_ldap_projects()

    try:
        default_role = ProjectRole.objects.get(name=DEFAULT_PROJECT_ROLE)
    except ProjectRole.DoesNotExist:
        raise Exception('Default Project Role does not exists. Please create it before running the import script.')

    for ldap_project in ldap_projects:
        if DEBUG: print('ldap_project=', ldap_project)
        # get project name and ldap_group
        try:
            project_name = ldap_project[1][PROJECT_ATTRIBUTES['name']][0].encode('ascii', 'ignore')
            print('\n Processing project: %s' % project_name)
            ldap_group = ldap_project[1]['cn'][0].encode('ascii', 'ignore')
            ldap_id = ldap_project[1]['gidNumber'][0].encode('ascii', 'ignore')
        except:
            add_error('Project without name', ldap_project)
            pass

        # retrieve or create project
        try:
            project = Project.objects.get(ldap_name=ldap_group)
        except Project.DoesNotExist:
            try:
                description = ldap_project[1][PROJECT_ATTRIBUTES['description']][0].encode('ascii', 'ignore')
            except:
                add_error('Project without description', project_name)
                description = "Not Provided"
            if DEBUG: print('project_description=', description)
            project = Project(ldap_name=ldap_group, ldap_id=ldap_id, abstract=description)
            project.ldap_id = ldap_id

        project.name = project_name
        if project.ldap_name.startswith('yproject'):
            project.environment = Project.ENV_YELLOW
        elif project.ldap_name.startswith('project'):
            project.environment = Project.ENV_GREEN
        project.status = Project.STATUS_ACTIVE
        project.instructors = DfRole.objects.get(ldap_name='instructors')

        project.save()

        previous_members = project.projectmember_set.all()
        # print('previous_members=', previous_members)
        # print('ldap_project=', ldap_project)

        current_members = []
        if PROJECT_ATTRIBUTES['members'] in ldap_project[1]:
            for ldap_member in get_members(ldap_project[1][PROJECT_ATTRIBUTES['members']]):
                if DEBUG: print('ldap_member=', ldap_member)
                # # FreeIPA
                # if USER_ATTRIBUTES['username'] + '=' in ldap_member:
                #     member_uid = ldap_member.split(USER_ATTRIBUTES['username'] + '=')[1].split(',')[0]
                # # ADRF - Open LDAP
                # else:
                #     member_uid = ldap_member
                try:
                    user = User.objects.get(ldap_name=ldap_member)
                except User.DoesNotExist:
                    add_error('ProjectMemberhsip - User.DoesNotExist', ldap_member)
                    pass
                else:
                    try:
                        project_member = ProjectMember.objects.get(member=user, project=project)
                    except ProjectMember.DoesNotExist:
                        project_member = ProjectMember(member=user, project=project)
                        project_member.role = default_role
                        project_member.start_date = TIME_NOW
                    finally:
                        if project_member.id is None or not project_member.active():
                            print '   > Member added/enabled: %s' % user
                        project_member.save()
                        current_members.append(ldap_member)
        else:
            add_error('Project has no members', project_name)
            print '   This project has no members.'

        print('   Members=%s' % len(current_members))
        for disabled_member in [pm for pm in previous_members if pm.member.username not in current_members]:
            if disabled_member.active():
                disabled_member.end_date = TIME_NOW
                disabled_member.save()
                print('   > Member disabled: %s' % disabled_member.member)


def import_datasets():
    for ldap_dataset in get_ldap_datasets():
        if DEBUG: print('ldap_dataset=', ldap_dataset)

        try:
            dataset_cn = ldap_dataset[1]['cn'][0].encode('ascii', 'ignore')
            ldap_id = ldap_dataset[1]['gidNumber'][0].encode('ascii', 'ignore')
            name = ldap_dataset[1][DATASET_ATTRIBUTES['ldap_name']][0].encode('ascii', 'ignore')
        except:
            add_error('Dataset without name', ldap_dataset)
            pass

        print '\n Processing Dataset: %s' % name
        try:
            description = ldap_dataset[1][DATASET_ATTRIBUTES['description']][0].encode('ascii', 'ignore')
        except:
            add_error('Dataset without description', dataset_cn)
            description = None

        # retrieve or create
        try:
            dataset = Dataset.objects.get(ldap_name=dataset_cn)
        except Dataset.DoesNotExist:
            dataset = Dataset(ldap_name=dataset_cn, ldap_id=ldap_id)
        dataset.description = description
        # doi <- name without 'dataset-'
        dataset.dataset_id = name.split(',')[0][8:]
        dataset.name = name.replace('-', ' ').title()
        dataset.ldap_id = ldap_id
        dataset.data_classification = Dataset.DATA_CLASSIFICATION_YELLOW
        dataset.save()

        # Get members of groups
        # print('ldap_dataset[1]=', ldap_dataset[1])
        # print('settings.LDAP_DATASET_FIELD_MEMBERS=', settings.LDAP_DATASET_FIELD_MEMBERS)
        if settings.LDAP_DATASET_FIELD_MEMBERS in ldap_dataset[1]:
            current_projects = get_members(ldap_dataset[1][settings.LDAP_DATASET_FIELD_MEMBERS])

            print '  Disabling old members:'
            for previous_access in dataset.datasetaccess_set.all():
                if previous_access.status() in \
                        (DatasetAccess.STATUS_APPROVED or DatasetAccess.STATUS_ACTIVE) \
                        and previous_access.project.ldap_name not in current_projects:
                    previous_access.expire_at = TIME_NOW
                    previous_access.save()
                    print '   > Disabled:', previous_access.project

            print '  Adding/Updating current permissions:', current_projects
            for project_name in current_projects:
                print '   > Project with access:', project_name
                try:
                    project = Project.objects.get(ldap_name=project_name)
                except Project.DoesNotExist:
                    add_error('[Dataset Access] Project does not exists', project_name)
                    continue

                try:
                    access = DatasetAccess.objects.get(dataset=dataset, project=project)
                except DatasetAccess.DoesNotExist:
                    access = DatasetAccess(dataset=dataset, project=project)
                    access.granted_at = TIME_NOW
                if not access.requested_at:
                    access.requested_at = TIME_NOW
                if not access.reviewed_at:
                    access.reviewed_at = TIME_NOW
                access.save()
        else:
            add_error('Dataset has no permissions', name)


def import_users():
    ldap_users = get_ldap_users()
    for ldap_user in ldap_users:
        try:
            username = ldap_user[1][USER_ATTRIBUTES['username']][0].encode('ascii', 'ignore')
            ldap_id = ldap_user[1][USER_ATTRIBUTES['ldap_id']][0].encode('ascii', 'ignore')
        except:
            add_error('User without username (%s)' % USER_ATTRIBUTES['username'], ldap_user)
            pass
        else:
            try:
                email = ldap_user[1][USER_ATTRIBUTES['email']][0].encode('ascii', 'ignore')
            except:
                email = '%s@undefined.adrf.info' % username
                add_error('User without email (%s)' % USER_ATTRIBUTES['email'], username)
            try:
                first_name = ldap_user[1][USER_ATTRIBUTES['first_name']][0].encode('ascii', 'ignore')
            except:
                first_name = MISSING_INFO_FLAG
                add_error('User without first name (%s)' % USER_ATTRIBUTES['first_name'], username)

            try:
                last_name = ldap_user[1][USER_ATTRIBUTES['last_name']][0].encode('ascii', 'ignore')
            except:
                last_name = MISSING_INFO_FLAG
                add_error('User without last name (%s)' % USER_ATTRIBUTES['last_name'], username)

            try:
                ldap_lock_time = ldap_user[1][USER_ATTRIBUTES['ldap_lock_time']][0].encode('ascii', 'ignore')
                ldap_lock_time = datetime.datetime.strptime(ldap_lock_time, "%Y%m%d%H%M%SZ")
                ldap_lock_time = ldap_lock_time.replace(tzinfo=pytz.utc)
            except:
                ldap_lock_time = None

            try:
                ldap_last_auth_time = ldap_user[1][USER_ATTRIBUTES['ldap_last_auth_time']][0].encode('ascii', 'ignore')
                ldap_last_auth_time = datetime.datetime.strptime(ldap_last_auth_time, "%Y%m%d%H%M%SZ")
                ldap_last_auth_time = ldap_last_auth_time.replace(tzinfo=pytz.utc)
            except:
                ldap_last_auth_time = None

            try:
                ldap_last_pwd_change = ldap_user[1][USER_ATTRIBUTES['ldap_last_pwd_change']][0].encode('ascii', 'ignore')
                ldap_last_pwd_change = datetime.datetime.strptime(ldap_last_pwd_change, "%Y%m%d%H%M%SZ")
                ldap_last_pwd_change = ldap_last_pwd_change.replace(tzinfo=pytz.utc)
            except:
                ldap_last_pwd_change = None

            if USER_ATTRIBUTES["ldap_ppolicy_configuration_dn"] in ldap_user[1]:
                system_user = True
            else:
                system_user = False

            try:
                user = User.objects.get(ldap_name=username)
                print("updating user '%s' ..." % username)
            except User.DoesNotExist:
                user = User(ldap_name=username,
                            ldap_id=ldap_id,
                            email=email,
                            first_name=first_name,
                            last_name=last_name)

                print("Creating user '%s' ..." % username)
            else:
                if not user.ldap_id == int(ldap_id):
                    user.ldap_id = ldap_id
                    message = "User '%s' ldap_id updated." % username
                    print(message)
                if not user.email == email:
                    user.email = email
                    message = "User '%s' email updated." % username
                    print(message)
                if not user.first_name == first_name:
                    user.first_name = first_name
                    message = "User '%s' first name updated." % username
                    print(message)
                if not user.last_name == last_name:
                    user.last_name = last_name
                    message = "User '%s' last name updated." % username
                    print(message)

            user.system_user = system_user
            user.ldap_lock_time = ldap_lock_time
            user.ldap_last_auth_time = ldap_last_auth_time
            user.ldap_last_pwd_change = ldap_last_pwd_change
            try:
                if USER_ATTRIBUTES['ldap_lock_time'] in ldap_user[1] and \
                                ldap_user[1][USER_ATTRIBUTES['ldap_lock_time']][0].encode('ascii', 'ignore') == "000001010000Z":
                    user.status = User.STATUS_DISABLED
                elif ldap_lock_time:
                    user.status = User.STATUS_LOCKED_WRONG_PASSWD
                else:
                    user.status = User.STATUS_ACTIVE
                user.save()
            except IntegrityError, ex:
                add_error('User UID duplicated %s (%s):' % (ldap_id, username), ex.message)

    message = "   > Users are synchronized."
    print(message)
    return


def run():
    print 'Start time:', TIME_NOW
    print('\n\nImporting Users...')
    import_users()

    print('\nImporting DfRoles (Groups) and membership...')
    import_groups()

    print('\nImporting Projects and membership...')
    import_projects()

    print('\nImporting Datasets and project permissions...')
    import_datasets()

    print('\n\n=== IMPORT SUMMARY ===')
    print('Total Users: %s' % User.objects.all().count())
    print('Total Projects: %s' % Project.objects.all().count())
    print('Total Roles (groups): %s' % DfRole.objects.all().count())
    print('Total User-Roles: %s' % UserDfRole.objects.all().count())
    print('Total Datasets: %s' % Dataset.objects.all().count())
    print('Total Dataset Access: %s' % DatasetAccess.objects.all().count())
    errors = ['{0}: {1}'.format(e, ERRORS[e]) for e in ERRORS]
    print '\033[31m LDAP Errors:\n > %s \033[0m' % '\n > '.join(sorted(errors))
    print('=== ============== ===')
