#!/usr/bin/env python
# From DjangoSnippets: https://djangosnippets.org/snippets/893/
import os

import ldap
from django.utils import timezone
from django.db.utils import IntegrityError
import shlex, argparse
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware
from django.conf import settings
from data_facility_admin.models import Project, User, ProjectMember, ProjectRole, DfRole, UserDfRole, ProfileTag

SEPARATOR=','
NO_USERNAME = '?'
ERROS = []

USER_STATUS = User.STATUS_PENDING_APPROVAL
TIME_NOW = timezone.now()

# INPUT_FILE = 'new_users.csv'


parser = argparse.ArgumentParser(description='Create accounts based on input file.', add_help=True)
parser.add_argument('--file', '-f',
                    help='Indicates the input CSV file that has account information. ' 
                            'The file should have the following columns: '
                            'first_name, last_name and email',
                    default=False, required=True)
parser.add_argument('--is_class', '-c', help='Indicates if the input file has class accounts. ' 
                                  'Class accounts should have a team column at the end.',
                    dest='is_class', action='store_const', const=True, default=False)
# parser.add_argument('--update', '-u', help='Update roles and projects for accounts if they exist',
#                     dest='update', action='store_const', const=True, default=False)
parser.add_argument('--team_name',
                    help='Base name for the teams.')
parser.add_argument('--projects', '-p',
                    help='Indicates to which project(s) to add the new accounts. '
                         'Multiple projects can be used.'
                         'This is specially useful for class accounts.',
                    nargs='+', default=None)
parser.add_argument('--roles', '-r',
                    help='Indicates to which role(s) to add the new accounts. '
                         'Multiple roles can be used. Default is "Students".',
                    nargs='+', default='Students')
parser.add_argument('--tags', '-t',
                    help='Indicates to which tag(s) to add the new accounts. '
                         'Multiple tags can be used.',
                    nargs='+', default=None)
parser.add_argument('--project_membership',
                    help='Indicates which project membership should be used.'
                         ' Default is "Student".',
                    choices=['Student', 'Owner', 'Member', 'Instructor'], default='Student')
parser.add_argument('--expiration', '-e',
                    help='Indicates when the new account roles and projects should expire. '
                         'Format: 2016-10-03T19:00:00',
                    default=None)
parser.add_argument('--member_projects',
                    help='Indicates to which project(s) to add the new accounts to as members. '
                         'Multiple projects can be used.',
                    nargs='+', default=None)


def run(*script_args):
    '''
    Example using docker-compose:
    docker-compose exec web python manage.py runscript create_accounts --script-args="-f accounts
        -r Students -p ada_18_uchi il_des_kcmo il_doc_kcmo kcmo_lehd -c -e 12/01/2018"

    :param script_args:
    :return:
    '''
    # Get args
    print('DFAdmin Script Create_Accounts')
    print('ARGS:' + str(script_args))
    try:
        split_args = shlex.split(script_args[0])
    except IndexError:
        split_args = []

    args = parser.parse_args(split_args)
    print('args:' + str(args))
    #args = None

    print 'Start time:', TIME_NOW
    errors = []
    file_name, is_class = init(args)

    # Create users, grant roles and projects
    create_users(file_name, is_class, errors)

    #Summary
    print('\n\n=== IMPORT SUMMARY ===')
    errors = ['{0}'.format(e) for e in errors]
    print '\033[31m Errors:\n > %s \033[0m' % '\n > '.join(sorted(errors))
    print('=== ============== ===')



def init(args):
    print('\n\nInit...')
    print('args=', args)
    arg_roles = args.roles
    args_project_membership = args.project_membership
    args_projects = args.projects
    args_expiration = args.expiration
    args_tags = args.tags
    args_team_name = args.team_name
    args_file_name = args.file
    args_is_class = args.is_class
    ##
    # arg_roles = ['Students']
    # args_project_membership = 'Student'
    # args_projects = ['ada_18_uchi', 'il_des_kcmo', 'il_doc_kcmo', 'kcmo_lehd']
    # args_expiration = '2018-12-31T00:00:00'
    # args_tags = ['class5']
    # args_team_name = 'ada_18_uchi'
    # args_file_name = 'accounts'
    # args_is_class = True

    # INIT ROLES
    try:
        global DF_ROLES
        DF_ROLES = [DfRole.objects.get(name=role_name) for role_name in arg_roles]
    except DfRole.DoesNotExist as ex:
        print('DFRole not found: ' + role_name)
        raise ex

    # Init PROJECTS
    try:
        global PROJECT_ROLE
        PROJECT_ROLE = ProjectRole.objects.get(name=args_project_membership)
    except ProjectRole.DoesNotExist as ex:
        print('ProjectRole not found: ' + args_project_membership)
        raise ex

    try:
        global PROJECTS
        PROJECTS = []
        if args_projects is not None and len(args_projects) > 0:
            for project_name in args_projects:
                PROJECTS.append(Project.objects.get(name=project_name))
        else:
            PROJECTS = None
    except Project.DoesNotExist as ex:
        print('ProjectRole not found: ' + project_name)
        raise ex

    global EXPIRATION_DATE
    if args_expiration:
        EXPIRATION_DATE = parse_datetime(args_expiration)
        # if not is_aware(EXPIRATION_DATE):
        #     EXPIRATION_DATE = make_aware(EXPIRATION_DATE)
    else:
        EXPIRATION_DATE = None

    global TAGS
    TAGS = []
    for tag in args_tags:
        try:
            tag = ProfileTag.objects.get(text=tag)
        except ProfileTag.DoesNotExist:
            tag = ProfileTag.objects.create(text=tag)
        TAGS.append(tag)

    global TEAM_NAME_BASE
    TEAM_NAME_BASE = args_team_name

    return args_file_name, args_is_class


def create_users(filename, class_file=False, errors=[]):
    print('\n\nCreating Users...')

    teams = {}
    with open(filename) as f:
        for line in f:
            values = line.strip().split(SEPARATOR)

            # Ignore header if it is in first line.
            if 'first_name' in values:
                continue

            print('Creating user: %s' % str(values))
            #Read from file
            if class_file:
                first_name, last_name, email, team = values
            else:
                first_name, last_name, email = values
                team = None

            # if username == NO_USERNAME:
            username = None
            try:
                if len(User.objects.filter(email=email)) > 0:
                        print('  Already exists. Skipping: {0}'.format(line))
                        # raise Exception('Skipping {0}. Already exists.'.format(line))
                else:
                    user = User(first_name=first_name,
                                last_name=last_name,
                                email=email,
                                status=USER_STATUS,
                                ldap_name=username)
                    user.save()

                    print('add_tags')
                    add_tags(user)

                    if team:
                        teams.get(team, []).append(user)

                    print('grant_roles')
                    grant_roles(user)
                    print('grant_projects')
                    grant_projects(user, team)
                    print('    > Success')


            except Exception as ex:
                # raise ex
                print('    > Error:', ex.message)
                errors.append(', '.join(values) + '\n - ' + ex.message)


def grant_roles(user):
    global DF_ROLES
    for df_role in DF_ROLES:
        UserDfRole(user=user, role=df_role, begin=TIME_NOW).save()


def grant_projects(user, team):
    global PROJECTS
    global PROJECT_ROLE
    global EXPIRATION_DATE
    global TIME_NOW

    for project in PROJECTS:
        ProjectMember(project=project,
                      member=user,
                      role=PROJECT_ROLE,
                      start_date=TIME_NOW,
                      end_date=EXPIRATION_DATE).save()

    try:
        global TEAM_NAME_BASE
        team_name = TEAM_NAME_BASE + str(team)
        team = Project.objects.get(name=team_name)
    except Project.DoesNotExist:
        team = Project(name=team_name, abstract='Team Project')
        team.save()

    ProjectMember(project=team,
                  member=user,
                  role=ProjectRole.objects.get(name='Member'),
                  start_date=TIME_NOW,
                  end_date=EXPIRATION_DATE).save()


def add_tags(user):
    global TAGS
    for tag in TAGS:
        user.tags.add(tag)
        user.save()


    # def run(*script_args):



    # print('ERRORS:', errors)




