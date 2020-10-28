from django.conf import settings
from storages.backends.azure_storage import AzureStorage


class AzureMediaStorage(AzureStorage):
    account_name = settings.AZ_STORAGE_ACCOUNT
    account_key = settings.AZ_STORAGE_KEY
    azure_container = settings.AZ_MEDIA_CONTAINER
    expiration_secs = None
    overwrite_files = True


class AzureStaticStorage(AzureStorage):
    account_name = settings.AZ_STORAGE_ACCOUNT
    account_key = settings.AZ_STORAGE_KEY
    azure_container = settings.AZ_STATIC_CONTAINER
    expiration_secs = None
