from .settings import *

# Debug mode should *never* be on in production
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
DEBUG = os.environ.get('DEBUG', False)

# Configure default domain name
ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']]

# Configure managed database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DJANGO_DATABASE_NAME'],
        'HOST': os.environ['DJANGO_DATABASE_SERVER'],
        'USER': os.environ['DJANGO_DATABASE_USER'],
        'PASSWORD': os.environ['DJANGO_DATABASE_PASSWORD'],
        'OPTIONS': {'sslmode': 'require'},
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

# Static files and media files configuration
DEFAULT_FILE_STORAGE = 'cloud_analysis_manager.backend.AzureMediaStorage'
STATICFILES_STORAGE = 'cloud_analysis_manager.backend.AzureStaticStorage'

AZURE_STORAGE_ACCOUNT = os.environ['AZURE_STORAGE_ACCOUNT']
AZURE_STORAGE_KEY = os.environ.get('AZURE_STORAGE_KEY', False)
AZURE_MEDIA_CONTAINER = os.environ.get('AZURE_MEDIA_CONTAINER', 'media')
AZURE_STATIC_CONTAINER = os.environ.get('AZURE_STATIC_CONTAINER', 'static')

AZURE_CUSTOM_DOMAIN = os.environ.get('AZURE_STORAGE_HOST', f'https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net')
STATIC_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_STATIC_CONTAINER}/'
MEDIA_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_MEDIA_CONTAINER}/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
