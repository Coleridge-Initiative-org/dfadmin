#import rest_framework_jwt.authentication as jwt_authentication
print("hi")
def jwt_get_username_from_payload_handler(payload):
    print('import')
    from django.contrib.auth.models import Group, User
    print("chegou aqui")

    if 'preferred_username' in payload:
        username = payload['preferred_username']
        if 'email' in payload:
            email = payload['email']
        else:
            email = username+'@dfadmin.local'
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username, is_active=True, email=email)
            user.save()

        # TODO: Add Groups

        return payload['preferred_username']
# jwt_authentication.jwt_get_username_from_payload = jwt_get_username_from_payload_handler
