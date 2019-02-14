from decouple import config
import logging
import requests

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


def create_database(project_tool):
    """
    Call the RDS Database API to create the database.
    :param project_tool: data_facility_admin.models.ProjectTool
    :return:
    """
    try:
        init_system_info(project_tool)

        params = {"project": project_tool.project.ldap_name,
                  "az": project_tool.system_info['db_az'],
                  "db_instance_class": project_tool.system_info['db_instance_class'],
                  }
        logger.debug("params = %s" % params)
        logger.info('Creating RDS for project: %s' % project_tool.project)
        response = requests.post(DATABASE_ENDPOINT, params)
        logger.debug("response: %s" % response)
        if response.status_code == 200:
            logger.info('Database deleted with success.')
        elif response.status_code == 403:
            logger.error('Database not deleted. Token is invalid. '
                         'Status code: {0}, message: {1}'.format(response.status_code, response.text))
        else:
            logger.error('Database not deleted. '
                         'Status code: {0}, message: {1}'.format(response.status_code, response.text))

    except Exception as ex:
        logger.error('Error deleting PG RDS for project %s' % project_tool.project.ldap_name, exc_info=True)


def delete_database(project_tool):
    try:
        logger.debug('delete_database for project %s' % project_tool.project.ldap_name)

        logger.info("'Deleting database for project '%s'" % project_tool.project.ldap_name)
        params = {"project": project_tool.project.ldap_name,
                  }
        response = requests.delete(DATABASE_ENDPOINT, params)
        logger.debug("response: %s" % response)
        if response.status_code == 200:
            logger.info('Database deleted with success.')
        elif response.status_code == 403:
            logger.error('Database not deleted. Token is invalid. '
                         'Status code: {0}, message: {1}'.format(response.status_code, response.text))
        else:
            logger.error('Database not deleted. '
                         'Status code: {0}, message: {1}'.format(response.status_code, response.text))

    except Exception as ex:
        logger.error('Error deleting PG RDS for project %s' % project_tool.project.ldap_name, exc_info=True)


def grant_access(project_membership):
    pass


def revoke_access(project_membership):
    pass