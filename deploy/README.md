# Deploy (Staging and Production)

The deployment was configured considering the post "Sane Django Development with Docker":http://www.pedaldrivenprogramming.com/2015/10/sane-django-development-with-docker/

The configuration for Staging and Production will use all the same files.
The only difference is the file `secret.txt` which on the production server is a different file.

## ADRF Deployment instructions

Stop NGINX and Supervisor before starting the deploy process.
Also, make a database backup.

Prepare project
```
git clone https://github.com/NYU-Chicago-data-facility/dfadmin.git
virtualenv env
source env/bin/activate
```

Install requirements
```
sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev
pip install -r deploy/requirements.txt
```

If offline (ansible):
```
pip install --no-index --find-links file://{{unpack_path}}/deps
```

Config NGINX and Supervisor
```
ln -s /opt/dfadmin/deploy/adrf/nginx-dfadmin.conf /etc/nginx/conf.d/
ln -s /opt/dfadmin/deploy/adrf/supervisor-dfadmin.conf /etc/supervisor/conf.d/ 
```

SSL certificates are expected to be on the folders:
```
/etc/ssl/certs/star.adrf.info.crt
/etc/ssl/private/star.adrf.info.pem
```

Deploy as root from the project folder. source env first.
```
python manage.py collectstatic --noinput
chown ubuntu:root -R /www/dfadmin
#chmod a+r -R /www/dfadmin
```

Migrate database & create superuser.
```
source env/bin/activate
python manage.py migrate --noinput
```

Restart NGINX and Supervisor.
```
service supervisor restart
service nginx reload
```

One time
```
python manage.py runscript import_from_ldap --settings data_facility.deploy_settings
python manage.py createsuperuser --settings data_facility.deploy_settings
```
Add dfadmin.adrf.info to /etc/hosts (workspace and local (to-test) ) 

# Notes

## NGINX Container

Would be interesting to separate the container that runs the application and the one that runs NGINX in the future. But it was done this way to facilitate the management and access to statics and media. A possible solution can be "Django Development With Docker Compose and Machine":https://realpython.com/blog/python/django-development-with-docker-compose-and-machine/ .

## Container for the application files

Instead of mounting the project folder on the containers, a docker volume should be used.

# Troubleshooting

* "Inspect error when building the image":http://stackoverflow.com/questions/26220957/how-can-i-inspect-the-file-system-of-a-failed-docker-build

# References:
* http://www.pedaldrivenprogramming.com/2015/10/sane-django-development-with-docker/
* https://docs.docker.com/compose/environment-variables/
