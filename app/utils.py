import sqlite3
from typing import Union

import storages.backends.gcloud
from django.core.files.storage import default_storage


class Sqlite:
    """Sqlite3 helper class which enables the ``with`` statement to open the
    database, get the cursor, commit transaction and close the database.

    Example:
        >>> with Sqlite('example.db') as cursor:
        ...     cursor.execute('SELECT * FROM stocks ORDER BY price')
        ...     print(cursor.fetchone())
    """

    def __init__(self, file):
        self.file = file

    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        self.conn.row_factory = sqlite3.Row
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


class GoogleCloudStorage:

    @staticmethod
    def check_file_exists(filename: str,
                          storage: storages.backends.gcloud.GoogleCloudStorage = default_storage) -> bool:
        """Check if the given file exists in gcs.

        Args:
            filename: Path to the file inside the bucket.
            storage: Storage backend to use. This sets which bucket is used.
        """
        return storage.exists(filename)

    @staticmethod
    def read_file(filename: str, storage: storages.backends.gcloud.GoogleCloudStorage = default_storage) -> bytes:
        """Read the given file from gcs.

        Args:
            filename: Path to the file inside the bucket.
            storage: Storage backend to use. This sets which bucket is used.
        """
        with storage.open(filename, 'r') as f:
            return f.read()

    @staticmethod
    def upload_file(filename: str,
                    file_content: Union[bytes, str],
                    storage: storages.backends.gcloud.GoogleCloudStorage = default_storage):
        """Upload the given file to gcs.

        Args:
            filename: Path to the file inside the bucket.
            file_content: The value written to the file.
            storage: Storage backend to use. This sets which bucket is used.
        """
        with storage.open(filename, 'w') as f:
            f.write(file_content)

    @staticmethod
    def delete_file(filename: str, storage: storages.backends.gcloud.GoogleCloudStorage = default_storage):
        """Delete the given file from gcs.

        Args:
            filename: Path to the file inside the bucket.
            storage: Storage backend to use. This sets which bucket is used.
        """
        storage.delete(filename)

    @staticmethod
    def get_url(filename: str, storage: storages.backends.gcloud.GoogleCloudStorage = default_storage) -> str:
        """Return the url for the Blob associated with the given file.

        Args:
            filename: Path to the file inside the bucket.
            storage: Storage backend to use. This sets which bucket is used.
        """
        return storage.url(filename)
