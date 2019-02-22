from decouple import config
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# TODO: The config should come from the .env file.
DEFAULT_CONFIG = {
    'region': config('RDS_DEFAULT_CONFIG__REGION', default='us-west'),
    'db_az': config('RDS_DEFAULT_CONFIG__DB_AZ', default='us-west-2a'),
    'db_instance_class': config('RDS_DEFAULT_CONFIG__DB_AZ', default='db.t3.micro'),
    'master_username': '?',
    'master_password': '?',
    'project_iam_role': '?',
    'key_id': '?',
}
RDS_API = config('RDS_API')
DATABASE_ENDPOINT = RDS_API + '/database'
DATABASE_PERMISSION_ENDPOINT = RDS_API + '/database_permission'
API_KEY = config('RDS_API_KEY')


ACTION_CREATE = 'create'
ACTION_DELETE = 'delete'
ACTIONS = {ACTION_CREATE, ACTION_DELETE}

STATUS_CREATED = 'Created'
STATUS_DELETED = 'Deleted'


def init_system_info(project_tool):
    """
    Creates base system_info for this tool if it is not setup yet.
    :param project_tool:
    :return:
    """
    if not project_tool.system_info:
        logger.debug("Initializing system info with default values.")
        project_tool.system_info = DEFAULT_CONFIG
        project_tool.save()


def call_api(action, api_endpoint, params):
    if not settings.RDS_INTEGRATION:
        logger.info('Not calling API as settings.RDS_INTEGRATION is %s' % settings.RDS_INTEGRATION)
        return None

    try:
        logger.debug("params = %s" % params)
        logger.info('Calling API {0} {1} with params: {2}'.format(action, api_endpoint, params))
        if action is ACTION_CREATE:
            response = requests.post(api_endpoint, params)
        elif action is ACTION_DELETE:
            response = requests.delete(api_endpoint, params)
        else:
            raise Exception('Unrecognized ACTION: %s. It must be one of %s' % (action, ACTIONS))

        logger.debug("response: %s" % response)
        if response.status_code == 200:
            logger.info('Database %s with success.' % action)
            return response.body

        elif response.status_code == 403:
            logger.error('%s Database failed. Token is invalid. '
                         'Status code: {0}, message: {1}'.format(action, response.status_code, response.text))

        elif response.content and 'message' in response.content \
                and response.content['message'] == 'Endpoint request timed out':
            error_message = '%s Database failed. Error %s.' % (action, response.content['message'])
            logger.error(error_message)
            raise Exception(error_message)

        else:
            logger.error('{0} Database failed. '
                         'Status code: {1}, message: {2}'.format(action, response.status_code, response.text))

    except Exception as ex:
        logger.error('Error creating PG RDS with params: ' % params, exc_info=True)
        raise ex


def create_database(project_tool):
    """
    Call the RDS Database API to create the database sending the database name and instance_type.
    Expected return from API call:
        {"project": "dfadmintestproject3",
         "kms_key": "28c70ede-5818-45e1-8f3f-a8e2e10cd27f",
         "db_instance_class": "db.t3.micro",
         "region": "us-east-1",
         "master_username": "dfadmintestproject3_master",
         "role_name": "adrf_dfadmintestproject3_role"}

    :param project_tool: data_facility_admin.models.ProjectTool
    :return:
    """
    init_system_info(project_tool)

    params = {"project": project_tool.project.ldap_name,
              "az": project_tool.system_info['db_az'],
              "db_instance_class": project_tool.system_info['db_instance_class'],
              }
    response = call_api(ACTION_CREATE, DATABASE_ENDPOINT, params)
    if response:
        project_tool.system_info['kms_key'] = response.get('kms_key')
        project_tool.system_info['master_username'] = response.get('master_username')
        project_tool.system_info['role_name'] = response.get('role_name')
        project_tool.system_info['rds_status'] = STATUS_CREATED


def delete_database(project_tool):
    """
       Call the RDS Database API to delete the database sending the database name.
       Expected return from API call:
           {"project": "dfadmintestproject3",
           "kms_key": "28c70ede-5818-45e1-8f3f-a8e2e10cd27f",
           "pending_window_in_days": 7,
           "region": "us-east-1"}

       :param project_tool: data_facility_admin.models.ProjectTool
       :return:
       """
    init_system_info(project_tool)
    params = {"project": project_tool.project.ldap_name}
    response = call_api(ACTION_DELETE, DATABASE_ENDPOINT, params)
    if response:
        project_tool.system_info['kms_key'] = response.get('kms_key')
        project_tool.system_info['pending_window_in_days'] = response.get('pending_window_in_days')
        project_tool.system_info['rds_status'] = STATUS_DELETED


def grant_access(project_membership):
    """
    Grant access to database based on project name and username.
    Expected API call response:
        { ... }
    :param project_membership:
    :return:
    """
    project_name = project_membership.project.ldap_name
    username = project_membership.member.ldap_name
    params = {'project': project_name, 'user': username}
    response = call_api(ACTION_CREATE, DATABASE_PERMISSION_ENDPOINT, params)


def revoke_access(project_membership):
    """
        Grant access to database based on project name and username.
        Expected API call response:
            { ... }

        :param project_membership:
        :return:
        """
    project_name = project_membership.project.ldap_name
    username = project_membership.member.ldap_name
    params = {'project': project_name, 'user': username}
    response = call_api(ACTION_DELETE, DATABASE_PERMISSION_ENDPOINT, params)