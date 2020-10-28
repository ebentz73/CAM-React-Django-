import logging
import os
import sqlite3
from typing import TypeVar, Generic, Iterator, IO, AnyStr

import docker
import requests
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import QuerySet

_Z = TypeVar('_Z')


class ModelType(Generic[_Z], QuerySet):
    def __iter__(self) -> Iterator[_Z]:
        pass


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


class StorageHelper:
    @staticmethod
    def check_file_exists(filename: str, storage=default_storage) -> bool:
        """Check if the specified file exists.

        Args:
            filename: The file to check.
            storage: The Django storage backend to use. Defaults to
                default_storage.
        """
        return storage.exists(filename)

    @staticmethod
    def read_file(filename: str, storage=default_storage) -> bytes:
        """Read the specified file from storage.

        Args:
            filename: The file to read.
            storage: The Django storage backend to use. Defaults to
                default_storage.
        """
        with storage.open(filename, 'r') as f:
            return f.read()

    @staticmethod
    def upload_file(
            filename: str, file_content: IO[AnyStr], storage=default_storage
    ):
        """Save the specified file to storage.

        Args:
            filename: The pathname of the file to be saved.
            file_content: The contents of the file.
            storage: The Django storage backend to use. Defaults to
                default_storage.
        """
        with storage.open(filename, 'w') as f:
            f.write(file_content)

    @staticmethod
    def delete_file(filename: str, storage=default_storage):
        """Delete the given file from Azure Storage Accounts.

        Args:
            filename: The file to delete.
            storage: The Django storage backend to use. Defaults to
                default_storage.
        """
        storage.delete(filename)

    @staticmethod
    def get_url(filename: str, expire=None, storage=default_storage) -> str:
        """Return a URL where the file's contents can be accessed.

        Args:
            filename: The file to access.
            expire: Number of seconds until the url expires.
            storage: The Django storage backend to use. Defaults to
                default_storage.
        """
        return storage.url(filename, expire=expire)


def is_cloud() -> bool:
    """Return ``True`` if web app is running in the cloud, otherwise ``False``."""
    return os.environ.get('DJANGO_ENV') in ('dev', 'prod')


def run_eval_engine_local(evaljob_id: int):
    from app.models import EvalJob

    tam_file = EvalJob.objects.get(pk=evaljob_id).solution.tam_file

    client = docker.APIClient(base_url='tcp://localhost:2375')

    environment = {
        'EVALJOB_CALLBACK': f'http://host.docker.internal:8000/api/evaljob/{evaljob_id}/',
    }

    volumes = [tam_file.path]

    host_config = client.create_host_config(binds=[f'{tam_file.path}:/app/{tam_file}'])

    container = client.create_container(
        image=settings.EVAL_ENGINE_IMAGE,
        environment=environment,
        volumes=volumes,
        host_config=host_config,
        detach=True,
    )

    client.start(container)


def run_eval_engine_cloud(evaljob_id: int):
    headers = {'x-functions-key': settings.AZ_FUNC_CREATE_ACI_KEY}

    data = {
        'location': 'southcentralus',
        'image': settings.EVAL_ENGINE_IMAGE,
        'memory': 8.0,
        'cpu': 2.0,
        'environment_variables': {
            'EVALJOB_CALLBACK': f'https://{settings.AZ_CUSTOM_DOMAIN}/api/evaljob/{evaljob_id}/',
        },
    }

    r = requests.post(
        settings.AZ_FUNC_CREATE_ACI, json=data, headers=headers,
    )
    try:
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(e)


run_eval_engine = run_eval_engine_cloud if is_cloud() else run_eval_engine_local
run_eval_engine.__doc__ = 'Run the eval engine container.'
