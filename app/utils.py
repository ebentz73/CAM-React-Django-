from django.core.files.storage import default_storage


def check_gcp_file_exists(file_name: str) -> bool:
    """Check if the given file exists in gcp storage.

    The bucket used is the one defined as the GS_BUCKET_NAME variable in
    settings.py."""
    return default_storage.exists(file_name)


def upload_file_to_gcp(file_name: str, file_content):
    """Upload the given file to gcp storage.

    The bucket used is the one defined as the GS_BUCKET_NAME variable in
    settings.py."""
    with default_storage.open(file_name, 'w') as f:
        f.write(file_content)


def delete_file_from_gcp(file_name: str):
    """Delete the given file from gcp storage.

    The bucket used is the one defined as the GS_BUCKET_NAME variable in
    settings.py."""
    default_storage.delete(file_name)


def get_gcp_url(file_name: str) -> str:
    """Return the url for the Blob associated with the given file.

    The bucket used is the one defined as the GS_BUCKET_NAME variable in
    settings.py"""
    return default_storage.url(file_name)
