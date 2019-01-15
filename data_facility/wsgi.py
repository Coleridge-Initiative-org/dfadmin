"""
WSGI config for data_facility project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

# import os
# SETTINGS = os.env("DJANGO_SETTINGS_MODULE")
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_facility.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
