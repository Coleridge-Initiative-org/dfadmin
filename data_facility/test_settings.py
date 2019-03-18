from settings import *

print('USING TEST SETTINGS...')
print('logging configuration is updated for tests: logs go to "FILE" only.')

RDS_INTEGRATION = False
WS_K8S_INTEGRATION = False

LOGGING['loggers']['data_facility_admin']['handlers'] = ['file']
LOGGING['loggers']['data_facility_integrations']['handlers'] = ['file']
