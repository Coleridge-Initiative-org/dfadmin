from settings import *

print('USING TEST SETTINGS...')

RDS_INTEGRATION = False
WS_K8S_INTEGRATION = False

LOGGING['loggers']['data_facility_admin']['handlers'] = ['file']
LOGGING['loggers']['data_facility_integrations']['handlers'] = ['file']
