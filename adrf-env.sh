#!/usr/bin/env bash

export LDAP_BASE_DN='dc=adrf,dc=info'
export LDAP_SERVER="ldap://auth.adrf.info"
export LDAP_ADMIN_GROUP="cn=admin-tech,cn=groups"
export LDAP_USER_SEARCH="ou=People"
export LDAP_GROUP_SEARCH="ou=Groups"