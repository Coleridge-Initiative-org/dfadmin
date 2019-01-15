#!/usr/bin/env bash
cd /opt/dfadmin && \
/opt/dfadmin/env/bin/python manage.py runscript ldap_import_part && \
/opt/dfadmin/env/bin/python manage.py runscript ldap_export
