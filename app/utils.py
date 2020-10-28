import json
import msal
import requests
import logging
import os
import sqlite3
from typing import TypeVar, Generic, Iterator, IO, AnyStr

import docker
import requests
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import QuerySet
from grafana_api.grafana_face import GrafanaFace

_Z = TypeVar('_Z')
env = environ.Env()


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


class PowerBI:
    SCOPE = ['https://analysis.windows.net/powerbi/api/.default']
    AUTHORITY = 'https://login.microsoftonline.com/organizations'
    solution = None

    def get_workspace_id(self):
        return self.solution.workspace_id

    def get_report_id(self):
        return self.solution.report_id

    def get_roles(self):
        return ['T', 'V']

    def get_username(self):
        return ""

    def get_client_secret(self):
        return env('POWERBI_CLIENT_SECRET')

    def get_client_id(self):
        return env('POWERBI_CLIENT_ID')

    def get_tenant_id(self):
        return env('POWERBI_TENANT_ID')

    def get_access_token(self):
        """Returns AAD token using MSAL"""

        try:
            authority = self.AUTHORITY.replace('organizations', self.get_tenant_id())
            clientapp = msal.ConfidentialClientApplication(self.get_client_id(),
                                                           client_credential=self.get_client_secret(),
                                                           authority=authority)

            # Retrieve Access token from cache if available
            response = clientapp.acquire_token_silent(scopes=self.SCOPE, account=None)
            if not response:
                # Make a client call if Access token is not available in cache
                response = clientapp.acquire_token_for_client(scopes=self.SCOPE)
            try:
                return response['access_token']
            except KeyError:
                raise Exception(response['error_description'])

        except Exception as ex:
            raise Exception('Error retrieving Access token\n' + str(ex))

    def get_embed_token(self, access_token):
        """Returns Embed token and Embed URL"""

        try:
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token}
            reporturl = 'https://api.powerbi.com/v1.0/myorg/groups/' + self.get_workspace_id() + '/reports/' + self.get_report_id()

            try:
                apiresponse = requests.get(reporturl, headers=headers)
            except Exception as ex:
                raise Exception('Error while retrieving report Embed URL\n')

            if not apiresponse:
                raise Exception(
                    'Error while retrieving report Embed URL\n' + apiresponse.reason + '\nRequestId: ' + apiresponse.headers.get(
                        'RequestId'))

            try:
                apiresponse = json.loads(apiresponse.text)
                embedurl = apiresponse['embedUrl']
                datasetId = apiresponse['datasetId']
            except Exception as ex:
                raise Exception('Error while extracting Embed URL from API response\n' + apiresponse.text)

            # Get embed token
            embedtokenurl = 'https://api.powerbi.com/v1.0/myorg/GenerateToken'
            body = {'datasets': [], 'identities': []}
            if datasetId != '':
                body['datasets'].append({'id': datasetId})
                body['identities'].append(
                    {'username': self.get_username(), "roles": self.get_roles(), "datasets": [datasetId]})

            if self.get_report_id() != '':
                body['reports'] = []
                body['reports'].append({'id': self.get_report_id()})

            if self.get_workspace_id() != '':
                body['targetWorkspaces'] = []
                body['targetWorkspaces'].append({'id': self.get_workspace_id()})

            try:

                # Generate Embed token for multiple workspaces, datasets, and reports. Refer https://aka.ms/MultiResourceEmbedToken
                apiresponse = requests.post(embedtokenurl, data=json.dumps(body), headers=headers)
            except:
                raise Exception('Error while invoking Embed token REST API endpoint\n')

            if not apiresponse:
                raise Exception(
                    'Error while retrieving report Embed URL\n' + apiresponse.reason + '\nRequestId: ' + apiresponse.headers.get(
                        'RequestId'))

            try:
                apiresponse = json.loads(apiresponse.text)
                embedtoken = apiresponse['token']
                embedtokenid = apiresponse['tokenId']
                tokenexpiry = apiresponse['expiration']
            except Exception as ex:
                raise Exception('Error while extracting Embed token from API response\n' + apiresponse.reason)

            response = {'embedToken': embedtoken, 'embedUrl': embedurl, 'tokenExpiry': tokenexpiry, 'reportId': self.get_report_id()}
            return response
        except Exception as ex:
            return {'errorMsg': str(ex)}, 500

    def run(self, solution):
        self.solution = solution
        access_token = self.get_access_token()
        return self.get_embed_token(access_token)


run_eval_engine = run_eval_engine_cloud if is_cloud() else run_eval_engine_local
run_eval_engine.__doc__ = 'Run the eval engine container.'
