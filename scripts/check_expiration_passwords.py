# #!/usr/bin/env python
# import ldap, os
# from datetime import datetime
# from datetime import timedelta
# from django.conf import settings
#
#
# __ldap_conn = ldap.initialize(settings.LDAP_SERVER)
# __ldap_conn.protocol_version = ldap.VERSION3
# __ldap_conn.simple_bind_s(settings.LDAP_SETTINGS['Connection']['BindDN'],
#                                    settings.LDAP_SETTINGS['Connection']['BindPassword'])
#
#
# def get_ldap_users():
#     search_filter = settings.USER_LDAP_MAP['username'] + "=*"
#
#     return get_from_ldap(settings.LDAP_USER_SEARCH, search_filter, ['pwdChangedTime'])
#
#
# def get_from_ldap(search_base, search_filter, values):
#     if not search_base:
#         base = settings.LDAP_BASE_DN
#     else:
#         base = "%s,%s" % (search_base, settings.LDAP_BASE_DN)
#     result_data = __ldap_conn.search_s(base, ldap.SCOPE_SUBTREE, search_filter, values)
#     return result_data
#
# if __name__ == '__main__':
#     print 'Start time:', datetime.now()
#     print('\n\nInit...')
#
#     resultado = get_ldap_users()
#
#     for item in resultado:
#         id_user = item[0]
#         data = item[1]
#         if data:
#             datetime_object = datetime.strptime(data['pwdChangedTime'][0], "%Y%m%d%H%M%SZ")
#             expire_date = datetime_object + timedelta(days=60)
#             end_date = datetime.now() + timedelta(days=4)
#             if expire_date < end_date:
#                 print('\n\nUser that needs to reset password:')
#                 print(id_user.split(',')[0])
#
#                 print('Expires in: ')
#                 print(expire_date)
#
#     print('=== ============== ===')
#
# #34.225.207.35   meat.adrf.info
