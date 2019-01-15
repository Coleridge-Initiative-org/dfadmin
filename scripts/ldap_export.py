from data_facility_admin.helpers import LDAPHelper

def run(*args):
    helper = LDAPHelper()
    helper.export_users()
    helper.export_projects()
    helper.export_df_roles()
    helper.export_datasets()
    helper.close()
