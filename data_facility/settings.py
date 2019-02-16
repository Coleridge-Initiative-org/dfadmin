"""
Django settings for data_facility project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os
import errno
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType
from decouple import config, Csv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

ENV = config('ENV', 'PRODUCTION')
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CHAR_FIELD_MAX_LENGTH = 256
TEXT_FIELD_MAX_LENGTH = 1024

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

if ENV == 'LOCAL':
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', cast=bool, default=True)
SESSION_COOKIE_SECURE = config('CSRF_SESSION_COOKIE_SECURE', cast=bool, default=True)

# DJANGO ADMIN CONFIG ------------------------------------------------------------------------------
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', cast=int, default=60*60*24)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool, default=False)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default=['dfadmin.adrf.info'])

# ADMINS and notification
ADMINS = [('Daniel Castellani', 'daniel.castellani@nyu.edu')]
MANAGERS = ADMINS
SEND_BROKEN_LINK_EMAILS = config('SEND_BROKEN_LINK_EMAILS', default=True)


# Email
EMAIL_HOST = config('EMAIL_HOST', default=None)
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default=None)
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default=None)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_FROM = config('EMAIL_FROM', default='dfadmin@adrf.info')
SERVER_EMAIL = EMAIL_FROM
DEFAULT_FROM_EMAIL = EMAIL_FROM

## --- ADRF ---
ADRF_MFA_ACTIVATED = config('ADRF_MFA_ACTIVATED', cast=bool, default=True)
ADRF_SYSTEM_NAME = config('ADRF_SYSTEM_NAME', default=None)

## --- DFADMIN
ADRF_URL = config('ADRF_URL')
WELCOME_EMAIL_KEYCLOAK_URL = config('ID_ADRF_URL')
PWD_RESET_INSTRUCTIONS = config('PWD_RESET_INSTRUCTIONS', default='???')
ADRF_PASS_EXPIRATION_TIME = config('ADRF_PASS_EXPIRATION_TIME', cast=int, default=60)
ADRF_ENABLE_CUSTOM_USERNAME = config('ADRF_ENABLE_CUSTOM_USERNAME', cast=bool, default=False)

# ----------------- DF Admin LDAP Configuration -------------------------
ADRF_ADMIN_GROUP = 'adrf-admin-grp'
LDAP_STAFF_GROUP = 'adrf-staff'
LDAP_BASE_DN = config('LDAP_BASE_DN', default='dc=adrf,dc=info')
LDAP_SERVER = config('LDAP_SERVER', default="ldaps://meat.adrf.info")
LDAP_USER_SEARCH = config('LDAP_USER_SEARCH', default="ou=People")
LDAP_GROUP_SEARCH = config('LDAP_GROUP_SEARCH', default="ou=Groups")
LDAP_DATASET_SEARCH = config('LDAP_DATASET_SEARCH', default="ou=Datasets")
LDAP_PROJECT_SEARCH = config('LDAP_PROJECT_SEARCH', default="ou=Projects")
LDAP_ADMIN_GROUP = "cn="+ADRF_ADMIN_GROUP+"," + LDAP_GROUP_SEARCH
LDAP_STAFF_GROUP = "cn="+LDAP_STAFF_GROUP+"," + LDAP_GROUP_SEARCH
#
AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = config('AUTH_LDAP_BIND_AS_AUTHENTICATING_USER',
                                               cast=bool,
                                               default=True)

# ----------------- DJANGO CONFIG -------------------------
INSTALLED_APPS = (
    'data_facility_admin',
    'data_facility_metadata',
    'admin_view_permission',
    'grappelli',
    'django.contrib.admin',
    # 'admin_reorder',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'simple_history',
    'rest_framework.authtoken',
    'rest_framework',
    'django_filters',
    'rest_framework_swagger',
    'ajax_select',
    'nested_admin',
    'corsheaders',
    'graphene_django',
    # 'django.contrib.admindocs.middleware.XViewMiddleware',
)

GRAPHENE = {
    'SCHEMA': 'data_facility.schema.schema' # Where your Graphene schema lives
}


MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
)

TEMPLATES = [
    {
        # 'DEBUG': DEBUG,
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
            # 'connect_timeout': 5,
        },
    },
]
# ----------------- ADMIN REORDER -------------------------
ADMIN_REORDER = (
    # Keep original label and models
    'sites',

    # Reorder app models
    {'app': 'data_facility_admin', 'label': 'People',
        'models': ('data_facility_admin.User',
                   'data_facility_admin.DfRole',
                   'data_facility_admin.TermsOfUse',
                   'data_facility_admin.SignedTermsOfUse',
                   'data_facility_admin.Training',
                   'data_facility_admin.UserTraining',
                   'data_facility_admin.ProfileTag',
                   )},
    {'app': 'data_facility_admin', 'label': 'Projects',
        'models': ('data_facility_admin.Project',
                   'data_facility_admin.ProjectRole',
                   'data_facility_admin.ProjectMember',
                   'data_facility_admin.ProjectTool',
                   )},
    {'app': 'data_facility_admin', 'label': 'Data',
     'models': ('data_facility_admin.Dataset',
                'data_facility_admin.DataProvider',
                'data_facility_admin.DataSteward',
                'data_facility_admin.DatabaseSchema',
                'data_facility_admin.DataAgreement',
                'data_facility_admin.DataAgreementSignature',
                'data_facility_admin.DatasetAccess',
                'data_facility_admin.Keyword',
                'data_facility_admin.DataClassification',
                )},
    {'app': 'data_facility_metadata'},
    {'app': 'auth', 'label': 'DF Admin - Authentication and Authorization'},
    {'app': 'authtoken', 'label': 'DFAdmin - API'},

)

# ----------------- DJANGO GRAPPELLI -------------------------
GRAPPELLI_ADMIN_TITLE = 'Data Facility Admin'

# ----------------- CORS Config for Vue -------------------------
# Based on: https://www.techiediaries.com/django-cors/
CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = (
    'http//:localhost',
    'http://docker.for.mac.localhost',
)

# ----------------- DJANGO AJAX SELECT -------------------------
AJAX_SELECT_BOOTSTRAP = True
AJAX_SELECT_INLINES = 'inline'

# ----------------- API: DJANGO REST FRAMEWORK -------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        # Only authenticated users
        'rest_framework.permissions.IsAdminUser',
        'rest_framework.permissions.IsAuthenticated',

        # Use Django's standard `django.contrib.auth` permissions,
        # or allow read-only access for unauthenticated users.
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',
                                'rest_framework.filters.SearchFilter',
                                'rest_framework.filters.OrderingFilter'
                                ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
}


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
    "ldap_ppolicy_configuration_dn": "pwdPolicySubentry",
    "ldap_last_pwd_change": "pwdChangedTime"

}

LDAP_GROUP_FIELD_MEMBERS = config('LDAP_GROUP_FIELD_MEMBERS', default="member")

PROJECT_LDAP_MAP = {
    "name": "name",
    "ldap_name": "cn",
    # "active_members+member|username": config('LDAP_PROJECT_FIELD_MEMBERS', default="memberUid"),
    "active_members+ldap_full_dn": LDAP_GROUP_FIELD_MEMBERS,
    "abstract": "summary",
    "created_at": "creationdate",
    "ldap_id": "gidNumber",
}

LDAP_DATASET_FIELD_MEMBERS = config('LDAP_DATASET_FIELD_MEMBERS', default="memberURL")

DATASET_LDAP_MAP = {
    "ldap_name": "cn",
    "active_members+ldap_full_dn": LDAP_GROUP_FIELD_MEMBERS,
    "ldap_id": "gidNumber",
}
GROUP_LDAP_MAP = {
    "ldap_name": "cn",
    # "active_users+user|username": config('LDAP_PROJECT_FIELD_MEMBERS', default="memberUid"),
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
        'SystemUserPpolicyConfig': "cn=system-users,ou=policies,dc=adrf,dc=info",
        'PpolicyLockDownDurationSeconds': 900 
    },
    'Connection': {
        'BindDN': config('LDAP_BIND_DN', default="cn=admin,dc=adrf,dc=info"),
        'BindPassword': config('LDAP_BIND_PASSWD', default="???"),
    }
}

KEYCLOAK = {
    'API_URL': config('ID_ADRF_URL'),
    'REALM': config('ID_ADRF_REALM', default='master'),
    'ADMIN_USERNAME': config('ID_ADRF_USER', default='***REMOVED***'),
    'ADMIN_PASSWORD': config('ID_ADRF_PASSWORD', default=''),
    'LDAP_ID': config('ID_ADRF_LDAP_ID', default=''),
}



# ----------------- LDAP Login Integration (BEGIN) -------------------------
# ref: https://pythonhosted.org/django-auth-ldap/example.html
# Baseline configuration.
AUTH_LDAP_SERVER_URI = LDAP_SERVER
AUTH_LDAP_BIND_DN = LDAP_SETTINGS['Connection']['BindDN']
AUTH_LDAP_BIND_PASSWORD = LDAP_SETTINGS['Connection']['BindPassword']
AUTH_LDAP_USER_SEARCH = LDAPSearch(LDAP_USER_SEARCH + ',' + LDAP_BASE_DN,
                                   ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

# Set up the basic group parameters.
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(LDAP_GROUP_SEARCH + ',' + LDAP_BASE_DN,
                                    ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)")
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": config('AUTH_LDAP_USER_ATTR_MAP_FIRST_NAME', default="givenName"),
    "last_name": config('AUTH_LDAP_USER_ATTR_MAP_SN', default="sn"),
    "email": config('AUTH_LDAP_USER_ATTR_MAP_MAIL', default="mail")
}
# Simple group restrictions
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": LDAP_STAFF_GROUP + ',' + LDAP_BASE_DN,
    "is_superuser": LDAP_ADMIN_GROUP + ',' + LDAP_BASE_DN,
}
# This is the default, but I like to be explicit.
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True

# To add cache and not hid LDAP as much
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = config('AUTH_LDAP_GROUP_CACHE_TIMEOUT',
                                       cast=int,
                                       default=5 * 60)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_auth_ldap.backend.LDAPBackend',
)
# import logging, logging.handlers
# logger = logging.getLogger('django_auth_ldap')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)
# ----------------- LDAP Login Integration (END) -------------------------

ROOT_URLCONF = 'data_facility.urls'

os.environ['DJANGO_SETTINGS_MODULE'] = 'data_facility.settings'
WSGI_APPLICATION = 'data_facility.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE', default='django.db.backends.postgresql_psycopg2'),
        'NAME':  config('DATABASES_NAME'),
        'USER': config('DATABASES_USER'),
        'PASSWORD': config('DATABASES_PASSWORD'),
        'HOST': config('DATABASES_HOST'),
        'PORT': config('DATABASES_PORT', cast=int, default=5432),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = config('TIME_ZONE', default='America/New_York')
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
DFADMIN_APP_HOME = config('DFADMIN_APP_HOME', default=None)
if DFADMIN_APP_HOME:
    APP_HOME = DFADMIN_APP_HOME
    STATIC_ROOT = APP_HOME + '/static'
    MEDIA_ROOT = APP_HOME + '/media'

STATIC_URL = '/static/'

# ''' Note on upgrading to Django 1.8
# https://docs.djangoproject.com/en/1.8/ref/templates/upgrading/ '''


LOGGING_LEVEL = config('LOGGING_LEVEL', default='DEBUG')
DJANGO_SERVER_LOGGING_LEVEL = LOGGING_LEVEL
LOG_LOCATION = config('LOG_LOCATION', default='logs/')
try:
    os.makedirs(LOG_LOCATION)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(LOG_LOCATION):
        pass

LOGIN_URL='/login'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        },
    },
    'handlers': {
        'console': {
                'level': DJANGO_SERVER_LOGGING_LEVEL,
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
        },
        'file': {
            'level': LOGGING_LEVEL,
            'class': 'logging.FileHandler',
            'filename': LOG_LOCATION + 'app.log',
        },
        'df_file': {
            'level': LOGGING_LEVEL,
            'class': 'logging.FileHandler',
            'filename': LOG_LOCATION + 'dfadmin-ldap.log',
            'formatter': 'verbose',
        },
        'django_auth_ldap_handler': {
            'level': LOGGING_LEVEL,
            'class': 'logging.FileHandler',
            'filename': LOG_LOCATION + 'django_auth_ldap.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'data_facility_metadata': {
            'handlers': ['file'],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
        'data_facility_admin': {
            'handlers': ['file'],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
        'django.server': {
            'handlers': ['console'],
            'level': DJANGO_SERVER_LOGGING_LEVEL,
            'propagate': False,
        },
        'django': {
            'handlers': ['file'],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
        'data_facility_admin': {
            'handlers': ['df_file'],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
        'django_auth_ldap': {
            'handlers': ['django_auth_ldap_handler'],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
    },
}

# SHELL_PLUS = "ipython"
SHELL_PLUS_MODEL_IMPORTS_RESOLVER = 'django_extensions.collision_resolvers.FullPathCR'
SHELL_PLUS_POST_IMPORTS = [
    # ('django.contrib.auth.models', 'User', 'DjangoUser'),
    ('data_facility_admin.factories', '*'),
    ('data_facility_admin.models', 'User'),
    ('rest_framework.authtoken.models', 'Token'),
]

print ('DEBUG=', DEBUG)
