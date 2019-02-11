# DFAdmin API

DFAdmin supports token authentication for the API clients. This API issupposed to be used only by services and **not users**.

It uses the Django Rest Framework Token Authentication. More details at 'tokenauthentication'(https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication.)

## Token Creation
Tokens are associated with (Django) Users on DFAdmin. First, create a user account and then assiciate a token with this user. Take note of the token as it should be saved on the clien service so it can authenticate with the API. 

First, run `make shell` or `./manage.py shell_plus` to open the Django Shell. Then, run the following code:
Step 1: Create the new service client account - also doable on the Admin UI.
```python 
    user_name = '<user_name>'
    user = django_contrib_auth_User.objects.create(username=user_name)
```
* Replace the `<username>` with the desired username. 

Step 2: Create API token
```python
token = Token.objects.create(user=user)
print('Token for user %s is "%s". ' % (user, token))
```

Step 3: **(Optional)** Add this user to read-only group. If you prefer to set the group and permissions on the Admin UI (preferred) skip the `Step 3`.
```python
group = Group.objects.get(name='ADRF Staff')
group.user_set.add(user)
``` 