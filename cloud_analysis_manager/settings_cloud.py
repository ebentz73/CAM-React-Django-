from .settings import *

EVAL_ENGINE_IMAGE = os.environ.get(
    'EVAL_ENGINE_IMAGE', 'crcam.azurecr.io/lonestar/trunavcore:latest'
)

AZ_FUNC_CREATE_ACI = os.environ.get('AZ_FUNC_CREATE_ACI')

AZ_FUNC_CREATE_ACI_KEY = os.environ.get('AZ_FUNC_CREATE_ACI_KEY')

# Debug mode should *never* be on in production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', SECRET_KEY)
DEBUG = os.environ.get('DJANGO_DEBUG', '').capitalize() == 'True'

# Configure default domain name
AZ_CUSTOM_DOMAIN = next(
    (
        os.environ[ev]
        for ev in ('AZ_CUSTOM_DOMAIN', 'WEBSITE_HOSTNAME')
        if ev in os.environ
    ),
    None,
)
ALLOWED_HOSTS = {os.environ['WEBSITE_HOSTNAME'], AZ_CUSTOM_DOMAIN}

# Configure managed database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DJANGO_DATABASE_NAME'],
        'HOST': os.environ['DJANGO_DATABASE_HOST'],
        'USER': os.environ['DJANGO_DATABASE_USER'],
        'PASSWORD': os.environ['DJANGO_DATABASE_PASSWORD'],
        'OPTIONS': {'sslmode': 'require'},
    }
}

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#         'LOCATION': 'cache_table',
#     }
# }

# Static files and media files configuration
DEFAULT_FILE_STORAGE = 'cloud_analysis_manager.backend.AzureMediaStorage'
STATICFILES_STORAGE = 'cloud_analysis_manager.backend.AzureStaticStorage'

AZ_STORAGE_ACCOUNT = os.environ['AZ_STORAGE_ACCOUNT']
AZ_STORAGE_KEY = os.environ.get('AZ_STORAGE_KEY')
AZ_MEDIA_CONTAINER = os.environ.get('AZ_MEDIA_CONTAINER', 'media')
AZ_STATIC_CONTAINER = os.environ.get('AZ_STATIC_CONTAINER', 'static')
AZ_STORAGE_HOST_SUFFIX = os.environ.get('AZ_STORAGE_HOST_SUFFIX', 'core.windows.net')
AZ_STORAGE_CUSTOM_HOST = os.environ.get(
    'AZ_STORAGE_CUSTOM_HOST', f'{AZ_STORAGE_ACCOUNT}.blob.{AZ_STORAGE_HOST_SUFFIX}'
)
STATIC_URL = f'https://{AZ_STORAGE_CUSTOM_HOST}/{AZ_STATIC_CONTAINER}/'
MEDIA_URL = f'https://{AZ_STORAGE_CUSTOM_HOST}/{AZ_MEDIA_CONTAINER}/'
