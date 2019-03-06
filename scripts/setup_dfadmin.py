# Author Daniel Castellani - daniel.castellani@nyu.edu
#
# This script populates the initial data required for DFAdmin and ADRF to work properly.
from django.contrib.auth.models import Group, Permission

from data_facility_admin.models import ProjectRole, DfRole

DF_ROLES = [
    {'name': 'Class Participant', 'desc': 'Class Participant',
     'ldap_name': None, 'ldap_id': 901},
    {'name': 'Instructor', 'desc': 'Class Instructor. Have access to all student projects.',
     'ldap_name': 'instructors', 'ldap_id': 902},
    {'name': 'Tech Admin', 'desc': 'ADRF Team 2 members', 'ldap_name': 'admin-tech',
     'ldap_id': 903},
    {'name': 'Export Reviewer', 'desc': 'Can review export requests.',
     'ldap_name': 'export-reviewers', 'ldap_id': 904},
    {'name': 'Data Provider', 'desc': '',
     'ldap_name': 'data-providers', 'ldap_id': 905},
    {'name': 'Other/Missing', 'desc': '',
     'ldap_name': None, 'ldap_id': 906},

    {'name': 'T13 Export Reviewer', 'desc': '',
     'ldap_name': 't13-export-reviewers', 'ldap_id': 907},
    {'name': 'T13 Tech Admin', 'desc': '',
     'ldap_name': 't13-admin-tech', 'ldap_id': 908},
    {'name': 'ADRF Staff', 'desc': 'Users with access to DFAdmin',
     'ldap_name': 'adrf-staff', 'ldap_id': 909},
]

PROJECT_ROLES = [
    {'name': 'Owner', 'system_role': ProjectRole.SYSTEM_ROLE_ADMIN},
    {'name': 'Student', 'system_role': ProjectRole.SYSTEM_ROLE_READER},
    {'name': 'Member', 'system_role': ProjectRole.SYSTEM_ROLE_WRITER},
    {'name': 'Instructor', 'system_role': ProjectRole.SYSTEM_ROLE_ADMIN},
]


def create_base_df_roles():
    for role in DF_ROLES:
        try:
            DfRole.objects.get(name=role['name'])
        except DfRole.DoesNotExist:
            df_role = DfRole(name=role['name'],
                             description=role['name'])
            df_role.ldap_name = role['ldap_name']
            df_role.ldap_id = role['ldap_id']
            df_role.save()


def create_base_project_roles():
    for pr in PROJECT_ROLES:
        try:
            ProjectRole.objects.get(name=pr['name'])
        except ProjectRole.DoesNotExist:
            role = ProjectRole(name=pr['name'],
                               description=pr['name'],
                               system_role=pr['system_role'])
            role.save()


def create_base_permissions_and_auth_groups():
    try:
        staff = Group.objects.get(name='ADRF Staff')
    except Group.DoesNotExist:
        staff = Group(name='ADRF Staff')
        staff.save()
    view_permissions = Permission.objects.filter(name__startswith='Can view')
    for permission in view_permissions:
        staff.permissions.add(permission)
    staff.save()

    print(' - ADRF Staff created.')

    try:
        managers = Group.objects.get(name='ADRF Managers')
    except Group.DoesNotExist:
        managers = Group(name='ADRF Managers')
        managers.save()
    managers.permissions.add(Permission.objects.get(name='Can add user',
                                                    content_type__model='user',
                                                 content_type__app_label='data_facility_admin'))
    managers.permissions.add(Permission.objects.get(name='Can change user',
                                                    content_type__model='user',
                                                 content_type__app_label='data_facility_admin'))
    managers.permissions.add(Permission.objects.get(name='Can add historical project',
                                                    content_type__model='historicalproject'))
    managers.permissions.add(Permission.objects.get(name='Can change historical project',
                                                    content_type__model='historicalproject'))
    managers.permissions.add(Permission.objects.get(name='Can view historicalproject',
                                                    content_type__model='historicalproject'))
    managers.permissions.add(Permission.objects.get(name='Can add historical project member',
                                                    content_type__model='historicalprojectmember'))
    managers.permissions.add(Permission.objects.get(name='Can change historical project member',
                                                    content_type__model='historicalprojectmember'))
    managers.permissions.add(Permission.objects.get(name='Can view historicalprojectmember',
                                                    content_type__model='historicalprojectmember'))
    managers.permissions.add(Permission.objects.get(name='Can add historical project role',
                                                    content_type__model='historicalprojectrole'))
    managers.permissions.add(Permission.objects.get(name='Can change historical project role',
                                                    content_type__model='historicalprojectrole'))
    managers.permissions.add(Permission.objects.get(name='Can view historicalprojectrole',
                                                    content_type__model='historicalprojectrole'))
    managers.permissions.add(Permission.objects.get(name='Can add historical project tool',
                                                    content_type__model='historicalprojecttool'))
    managers.permissions.add(Permission.objects.get(name='Can change historical project tool',
                                                    content_type__model='historicalprojecttool'))
    managers.permissions.add(Permission.objects.get(name='Can view historicalprojecttool',
                                                    content_type__model='historicalprojecttool'))
    managers.permissions.add(Permission.objects.get(name='Can add historical user',
                                                    content_type__model='historicaluser'))
    managers.permissions.add(Permission.objects.get(name='Can change historical user',
                                                    content_type__model='historicaluser'))
    managers.permissions.add(Permission.objects.get(name='Can view historicaluser',
                                                    content_type__model='historicaluser'))
    managers.permissions.add(Permission.objects.get(name='Can add historical user df role',
                                                    content_type__model='historicaluserdfrole'))
    managers.permissions.add(Permission.objects.get(name='Can change historical user df role',
                                                    content_type__model='historicaluserdfrole'))
    managers.permissions.add(Permission.objects.get(name='Can view historicaluserdfrole',
                                                    content_type__model='historicaluserdfrole'))
    managers.permissions.add(Permission.objects.get(name='Can add historical user training',
                                                    content_type__model='historicalusertraining'))
    managers.permissions.add(Permission.objects.get(name='Can change historical user training',
                                                    content_type__model='historicalusertraining'))
    managers.permissions.add(Permission.objects.get(name='Can view historicalusertraining',
                                                    content_type__model='historicalusertraining'))
    managers.permissions.add(Permission.objects.get(name='Can add project',
                                                    content_type__model='project'))
    managers.permissions.add(Permission.objects.get(name='Can change project',
                                                    content_type__model='project'))
    managers.permissions.add(Permission.objects.get(name='Can view project',
                                                    content_type__model='project'))
    managers.permissions.add(Permission.objects.get(name='Can add project member',
                                                    content_type__model='projectmember'))
    managers.permissions.add(Permission.objects.get(name='Can change project member',
                                                    content_type__model='projectmember'))
    managers.permissions.add(Permission.objects.get(name='Can view projectmember',
                                                    content_type__model='projectmember'))
    managers.permissions.add(Permission.objects.get(name='Can add project role',
                                                    content_type__model='projectrole'))
    managers.permissions.add(Permission.objects.get(name='Can change project role',
                                                    content_type__model='projectrole'))
    managers.permissions.add(Permission.objects.get(name='Can view projectrole',
                                                    content_type__model='projectrole'))
    managers.permissions.add(Permission.objects.get(name='Can add project tool',
                                                    content_type__model='projecttool'))
    managers.permissions.add(Permission.objects.get(name='Can change project tool',
                                                    content_type__model='projecttool'))
    managers.permissions.add(Permission.objects.get(name='Can view projecttool',
                                                    content_type__model='projecttool'))
    managers.permissions.add(Permission.objects.get(name='Can add user',
                                                    content_type__model='user',
                                                 content_type__app_label='data_facility_admin'))
    managers.permissions.add(Permission.objects.get(name='Can change user',
                                                    content_type__model='user',
                                                 content_type__app_label='data_facility_admin'))
    managers.permissions.add(Permission.objects.get(name='Can view user',
                                                    content_type__model='user',
                                                 content_type__app_label='data_facility_admin'))
    managers.permissions.add(Permission.objects.get(name='Can add user df role',
                                                    content_type__model='userdfrole'))
    managers.permissions.add(Permission.objects.get(name='Can change user df role',
                                                    content_type__model='userdfrole'))
    managers.permissions.add(Permission.objects.get(name='Can view userdfrole',
                                                    content_type__model='userdfrole'))
    managers.permissions.add(Permission.objects.get(name='Can add user training',
                                                    content_type__model='usertraining'))
    managers.permissions.add(Permission.objects.get(name='Can change user training',
                                                    content_type__model='usertraining'))
    managers.permissions.add(Permission.objects.get(name='Can view usertraining',
                                                    content_type__model='usertraining'))
    managers.save()
    print(' - ADRF Managers created')

    try:
        curators = Group.objects.get(name='ADRF Curators')
    except Group.DoesNotExist:
        curators = Group(name='ADRF Curators')
        curators.save()
    curators.permissions.add(Permission.objects.get(name='Can add data agreement',
                                                    content_type__model='dataagreement'))
    curators.permissions.add(Permission.objects.get(name='Can change data agreement',
                                                    content_type__model='dataagreement'))
    curators.permissions.add(Permission.objects.get(name='Can delete data agreement',
                                                    content_type__model='dataagreement'))
    curators.permissions.add(Permission.objects.get(name='Can view dataagreement',
                                                    content_type__model='dataagreement'))
    curators.permissions.add(Permission.objects.get(name='Can add data agreement signature',
                                                    content_type__model='dataagreementsignature'))
    curators.permissions.add(Permission.objects.get(name='Can change data agreement signature',
                                                    content_type__model='dataagreementsignature'))
    curators.permissions.add(Permission.objects.get(name='Can view dataagreementsignature',
                                                    content_type__model='dataagreementsignature'))
    curators.permissions.add(Permission.objects.get(name='Can add database schema',
                                                    content_type__model='databaseschema'))
    curators.permissions.add(Permission.objects.get(name='Can change database schema',
                                                    content_type__model='databaseschema'))
    curators.permissions.add(Permission.objects.get(name='Can view databaseschema',
                                                    content_type__model='databaseschema'))
    curators.permissions.add(Permission.objects.get(name='Can add data provider',
                                                    content_type__model='dataprovider'))
    curators.permissions.add(Permission.objects.get(name='Can change data provider',
                                                    content_type__model='dataprovider'))
    curators.permissions.add(Permission.objects.get(name='Can view dataprovider',
                                                    content_type__model='dataprovider'))
    curators.permissions.add(Permission.objects.get(name='Can add dataset',
                                                    content_type__model='dataset'))
    curators.permissions.add(Permission.objects.get(name='Can change dataset',
                                                    content_type__model='dataset'))
    curators.permissions.add(Permission.objects.get(name='Can view dataset',
                                                    content_type__model='dataset'))
    curators.permissions.add(Permission.objects.get(name='Can add dataset access',
                                                    content_type__model='datasetaccess'))
    curators.permissions.add(Permission.objects.get(name='Can change dataset access',
                                                    content_type__model='datasetaccess'))
    curators.permissions.add(Permission.objects.get(name='Can view datasetaccess',
                                                    content_type__model='datasetaccess'))
    curators.permissions.add(Permission.objects.get(name='Can add data steward',
                                                    content_type__model='datasteward'))
    curators.permissions.add(Permission.objects.get(name='Can change data steward',
                                                    content_type__model='datasteward'))
    curators.permissions.add(Permission.objects.get(name='Can view datasteward',
                                                    content_type__model='datasteward'))
    curators.permissions.add(Permission.objects.get(name='Can add historical data agreement',
                                                    content_type__model='historicaldataagreement'))
    curators.permissions.add(Permission.objects.get(name='Can change historical data agreement',
                                                    content_type__model='historicaldataagreement'))
    curators.permissions.add(Permission.objects.get(name='Can view historicaldataagreement',
                                                    content_type__model='historicaldataagreement'))
    curators.permissions.add(
        Permission.objects.get(name='Can add historical data agreement signature',
                               content_type__model='historicaldataagreementsignature'))
    curators.permissions.add(
        Permission.objects.get(name='Can change historical data agreement signature',
                               content_type__model='historicaldataagreementsignature'))
    curators.permissions.add(
        Permission.objects.get(name='Can delete historical data agreement signature',
                               content_type__model='historicaldataagreementsignature'))
    curators.permissions.add(
        Permission.objects.get(name='Can view historicaldataagreementsignature',
                               content_type__model='historicaldataagreementsignature'))
    curators.permissions.add(Permission.objects.get(name='Can add historical database schema',
                                                    content_type__model='historicaldatabaseschema'))
    curators.permissions.add(Permission.objects.get(name='Can change historical database schema',
                                                    content_type__model='historicaldatabaseschema'))
    curators.permissions.add(Permission.objects.get(name='Can view historicaldatabaseschema',
                                                    content_type__model='historicaldatabaseschema'))
    curators.permissions.add(Permission.objects.get(name='Can add historical dataset',
                                                    content_type__model='historicaldataset'))
    curators.permissions.add(Permission.objects.get(name='Can change historical dataset',
                                                    content_type__model='historicaldataset'))
    curators.permissions.add(Permission.objects.get(name='Can view historicaldataset',
                                                    content_type__model='historicaldataset'))
    curators.permissions.add(Permission.objects.get(name='Can add historical data steward',
                                                    content_type__model='historicaldatasteward'))
    curators.permissions.add(Permission.objects.get(name='Can change historical data steward',
                                                    content_type__model='historicaldatasteward'))
    curators.permissions.add(Permission.objects.get(name='Can view historicaldatasteward',
                                                    content_type__model='historicaldatasteward'))
    curators.permissions.add(Permission.objects.get(name='Can add ldap object',
                                                    content_type__model='ldapobject'))
    curators.permissions.add(Permission.objects.get(name='Can change ldap object',
                                                    content_type__model='ldapobject'))
    curators.permissions.add(Permission.objects.get(name='Can view ldapobject',
                                                    content_type__model='ldapobject'))
    curators.save()
    print(' - ADRF Curators created')


def run():
    print("Loading Base Data Facility Roles")
    create_base_df_roles()
    print("Loading Base Permissions")
    create_base_permissions_and_auth_groups()
    print("Loading Base Data Project Roles")
    create_base_project_roles()
    print("Initial data loaded with success.")
