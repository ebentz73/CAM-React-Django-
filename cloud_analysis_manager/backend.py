from django.conf import settings
from storages.backends.azure_storage import AzureStorage


class AzureMediaStorage(AzureStorage):
    account_name = settings.AZ_STORAGE_ACCOUNT
    account_key = settings.AZ_STORAGE_KEY
    azure_container = settings.AZ_MEDIA_CONTAINER
    custom_domain = settings.AZ_STORAGE_CUSTOM_HOST
    endpoint_suffix = settings.AZ_STORAGE_HOST_SUFFIX
    expiration_secs = 600
    overwrite_files = True


class AzureStaticStorage(AzureStorage):
    account_name = settings.AZ_STORAGE_ACCOUNT
    account_key = settings.AZ_STORAGE_KEY
    azure_container = settings.AZ_STATIC_CONTAINER
    custom_domain = settings.AZ_STORAGE_CUSTOM_HOST
    endpoint_suffix = settings.AZ_STORAGE_HOST_SUFFIX
    expiration_secs = None
