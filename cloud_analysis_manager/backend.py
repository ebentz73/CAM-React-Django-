from django.conf import settings
from storages.backends.azure_storage import AzureStorage


class AzureMediaStorage(AzureStorage):
    custom_domain = settings.AZ_STORAGE_HOST
    account_name = settings.AZ_STORAGE_ACCOUNT
    account_key = settings.AZ_STORAGE_KEY
    azure_container = settings.AZ_MEDIA_CONTAINER
    expiration_secs = 600
    overwrite_files = True


class AzureStaticStorage(AzureStorage):
    custom_domain = settings.AZ_STORAGE_HOST
    account_name = settings.AZ_STORAGE_ACCOUNT
    account_key = settings.AZ_STORAGE_KEY
    azure_container = settings.AZ_STATIC_CONTAINER
    expiration_secs = None
