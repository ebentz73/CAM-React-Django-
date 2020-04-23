import json
import sqlite3
from typing import Union, TypeVar, Generic, Iterator

import docker
import environ
import storages.backends.gcloud
from django.core.files.storage import default_storage
from django.db.models import QuerySet
from grafana_api.grafana_face import GrafanaFace


_Z = TypeVar('_Z')


class ModelType(Generic[_Z], QuerySet):
    def __iter__(self) -> Iterator[_Z]:
        ...


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


def run_eval_engine(evaljob_id: int):
    env = environ.Env()

    # Run eval engine docker container for eval job
    client = docker.APIClient(base_url='tcp://localhost:2375')
    container = client.create_container('trunavconsolecore:latest',
                                        detach=True,
                                        environment={
                                            'EVALJOB_ID': evaljob_id,
                                            'EVALJOBDEF_URL': f'http://host.docker.internal:8000/api/evaljob/{evaljob_id}/',
                                            'RESULTS_URL': 'http://host.docker.internal:8000/api/results/',
                                            'GOOGLE_APPLICATION_CREDENTIALS': '/credentials.json'},
                                        volumes=['/credentials.json'],
                                        host_config=client.create_host_config(
                                            binds=[
                                                f"{env('GOOGLE_APPLICATION_CREDENTIALS')}:/credentials.json"
                                            ]
                                        ))
    client.start(container)


def create_dashboard(title: str) -> dict:
    """Create a new dashboard by duplicating the template dashboard.

    Args:
        title: Title of the new dashboard.

    Returns:
        Json response of the created dashboard.
    """
    env = environ.Env()

    grafana_api = GrafanaFace(auth=env('GRAFANA_API_KEY'), host=env('GRAFANA_HOST'))
    with open(env('GRAFANA_TEMPLATE')) as f:
        dashboard = json.load(f)
    dashboard['title'] = title
    return grafana_api.dashboard.update_dashboard({'dashboard': dashboard})
