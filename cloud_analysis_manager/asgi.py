"""
ASGI config for cloud_analysis_manager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.asgi import get_asgi_application

if os.environ.get('DJANGO_ENV') in ('dev', 'prod'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_analysis_manager.settings_cloud')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_analysis_manager.settings')

application = get_asgi_application()
