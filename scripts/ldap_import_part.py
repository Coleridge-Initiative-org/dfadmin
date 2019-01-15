from data_facility_admin.helpers import LDAPHelper

def run(*args):
    helper = LDAPHelper()
    helper.import_users()
    helper.import_datasets()
    helper.close()
