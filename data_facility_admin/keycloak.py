from urlparse import urljoin

import requests
import os
import logging

class KeycloakAPI(object):

    def __init__(self, url, realm, login, password):
        self.token = None
        self.realm = realm
        self.logger = logging.getLogger(__name__)

        self.keycloak_api = urljoin(url, '/auth/admin/')
        request_data = {'username': login, 'password': password, 'grant_type': 'password',
                        'client_id': 'admin-cli'}
        req = requests.post(urljoin(url, os.path.join('auth/realms/', os.path.join('master',
                                    'protocol/openid-connect/token'))), data=request_data,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'})

        if (req.status_code == 200):
            self.token = req.json()['access_token']
        else:
            raise Exception("Keycloak Login has failed. [Username=%s]" % login)

    def get_default_headers(self):
        return {'Authorization': 'Bearer %s' % self.token}

    def get_keycloak_api_with_realm(self):
        urljoin(self.keycloak_api, self.realm)

    def is_authenticated(self):
        return self.token is not None

    def ldap_full_sync(self, ldap_instance_id):
        if not self.is_authenticated():
            raise Exception("The Keycloak API service is not authenticated")
        else:
            req = requests.post(urljoin(self.keycloak_api, os.path.join('realms', self.realm,
                                                                        'user-storage',
                                                                        ldap_instance_id, 'sync')),
                                params={'action': 'triggerFullSync'},
                                headers=self.get_default_headers())
            return req.status_code == 200


    """
    [
        {
            "username": "ralves",
            "firstName": "Rafael",
            "emailVerified": false,
            "requiredActions": [],
            "enabled": true,
            "email": "rafa.ladis@gmail.com",
            "createdTimestamp": 1498000945438,
            "totp": true,
            "federationLink": "45be8282-9dfd-4459-a1fb-9037f154b706",
            "lastName": "Alves",
            "attributes": {
                "LDAP_ENTRY_DN": [
                    "uid=ralves,ou=People,dc=adrf,dc=info"
                ],
                "createTimestamp": [
                    "20170704193745Z"
                ],
                "uidNumber": [
                    "13013"
                ],
                "LDAP_ID": [
                    "ralves"
                ],
                "modifyTimestamp": [
                    "20170804221039Z"
                ]
            },
            "id": "ea6f55e9-1a80-4a38-864a-39c62f43782a"
        }
    ]
    """
    def get_keycloak_user(self, search_term):
        if not self.is_authenticated():
            raise Exception("The Keycloak API service is not authenticated")
        else:
            req = requests.get(urljoin(self.keycloak_api, os.path.join('realms', self.realm, 'users')),
                               params={'search': search_term}, headers=self.get_default_headers())

            if req.status_code == 200:
                return req.json()
            else:
                raise Exception("The Keycloak API service STATUS code is " + str(req.status_code))

    def reset_user_password(self, user_id, password, temporary):
        if not self.is_authenticated():
            raise Exception("The Keycloak API service is not authenticated")
        else:
            request_json = {'type': 'password', 'value': password, 'temporary': temporary }
            req = requests.put(urljoin(self.keycloak_api, os.path.join('realms', self.realm, 'users',
                                                                       user_id, 'reset-password')),
                               json=request_json, headers=self.get_default_headers())

            return req.status_code == 204

    """"
    Get the user from the get_keycloak_user method and update it, this method should receive 
    the updated json gotten from get_keycloak_user. In order to update the required actions, 
    add to the json a property called "requiredActions" with an array with the names of the 
    required actions ["CONFIGURE_TOTP", "UPDATE_PASSWORD", "UPDATE_PROFILE", "VERIFY_EMAIL", 
    "terms_and_conditions"]
    """
    def update_keycloak_user(self, user_id, user_json):
        if not self.is_authenticated():
            raise Exception("The Keycloak API service is not authenticated")
        else:
            req = requests.put(urljoin(self.keycloak_api, os.path.join('realms', self.realm, 'users',
                                                                       user_id)),
                               json=user_json, headers=self.get_default_headers())
            return req.status_code == 204


