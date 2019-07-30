''' tests for the serializers '''
# from django.test import TestCase
from unittest import TestCase, main
from .serializers import _get_attr_value, UserLDAPSerializer
from .models import User
from django.conf import settings

LDAP_USER_EXAMPLE = ('uid=chiahsuanyang,ou=People,dc=adrf,dc=info',
                     {
                         'gidNumber': ['502'],
                         'givenName': ['Chia-Hsuan'],
                         'homeDirectory': ['/nfshome/chiahsuanyang'],
                         'loginShell': ['/bin/bash'],
                         'objectClass': ['inetOrgPerson', 'posixAccount', 'top', 'adrfPerson'],
                         'uid': ['chiahsuanyang'],
                         'uidNumber': ['1039'],
                         'mail': ['cy1138@nyu.edu'],
                         'sn': ['Yang'],
                         'cn': ['Chia-Hsuan Yang'],
                     }
                    )

LDAP_PROJECT_EXAMPLE = ('cn=project-Food Analysis,ou=Projects,dc=adrf,dc=info',
                        {
                            'objectClass': ['posixGroup', 'groupOfMembers', 'adrfProject'],
                            'summary': ['required field'],
                            'name': ['Food Analysis'],
                            'gidNumber': ['7003'],
                            'creationdate': ['20161130221426Z'],
                            'cn': ['project-Food Analysis'],
                            'memberUid': ['rafael', 'will'],
                        }
                       )

LDAP_DFROLE_EXAMPLE = ('cn=annotation-reviewers,ou=Groups,dc=adrf,dc=info',
                       {
                           'objectClass': ['posixGroup', 'groupOfMembers'],
                           'gidNumber': ['5004'],
                           'cn': ['annotation-reviewers'],
                           'memberUid': ['rafael', 'will'],
                       }
                      )


class LdapSerializersTests(TestCase):
    ''' Tests for ldap serializers '''

    def setUp(self):
        self.user_dc = User(first_name='Daniel',
                            last_name='Castellani',
                            email='daniel.castellani@nyu.edu',
                            ldap_id=1000,
                            ldap_name='danielcastellani')
        self.ldap_user = UserLDAPSerializer.dumps(self.user_dc)
        # print('ldap_user=', self.ldap_user)

    def test_user_ldap_serializer_dump_uid(self):
        self.assertEqual(self.user_dc.username, self.ldap_user[1]['uid'][0])

    def test_user_ldap_serializer_dump_sn(self):
        self.assertEqual(self.user_dc.last_name, self.ldap_user[1]['sn'][0])

    def test_user_ldap_serializer_dump_cn(self):
        self.assertEqual(self.user_dc.full_name(), self.ldap_user[1]['cn'][0])

    def test_user_ldap_serializer_dump_mail(self):
        self.assertEqual(self.user_dc.email, self.ldap_user[1]['mail'][0])

    def test_user_ldap_serializer_dump_given_name(self):
        self.assertEqual(self.user_dc.first_name, self.ldap_user[1]['givenName'][0])

    def test_user_ldap_serializer_dump_home_dir(self):
        self.assertEqual('/nfshome/' + self.user_dc.username,
                         self.ldap_user[1]['homeDirectory'][0])

    def test_user_ldap_serializer_dump_gidNumber(self):
        self.assertEqual(self.user_dc.ldap_id, int(self.ldap_user[1]['gidNumber'][0]))

    def test_user_ldap_serializer_dump_dn(self):
        self.assertEqual('uid=%s,ou=People,%s' % (self.user_dc.ldap_name, settings.LDAP_BASE_DN), self.ldap_user[0])


if __name__ == '__main__':
    main()
