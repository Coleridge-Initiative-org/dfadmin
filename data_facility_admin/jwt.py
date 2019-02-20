from django.contrib.auth.models import Group, Permission, User
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication

class HappyAuthentication(BaseJSONWebTokenAuthentication):
    def jwt_get_username_from_payload(payload):
        print("chegou aqui")
        if 'preferred_username' in payload:
            username = payload['preferred_username']
            if 'email' in payload:
                email = pauyload['email']
            else:
                email = username+'@dfadmin.local'
            try:
                User.objects.get(username=username)
                #TODO GROUPS
            except User.DoesNotExist:
                user = User(username=username, is_active=True , email=email, staff=True)
                user.save()
            return payload['preferred_username']
