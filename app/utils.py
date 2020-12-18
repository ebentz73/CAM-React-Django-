import json
import logging
import os
import sqlite3
from typing import AnyStr, Generic, IO, Iterator, TypeVar

import docker
import msal
import requests
from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.files.storage import default_storage
from django.db.models import QuerySet
from grafana_api.grafana_face import GrafanaFace
from guardian.shortcuts import assign_perm, remove_perm, get_perms_for_model

from profile.models import Role

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
        kwargs = {'expire': expire} if is_cloud() else {}
        return storage.url(filename, **kwargs)


def is_cloud() -> bool:
    """Return ``True`` if web app is running in the cloud, otherwise ``False``."""
    return os.environ.get('DJANGO_ENV') in ('dev', 'prod')


def run_eval_engine(solution_pk: int, scenario_pk: int):
    """Run the eval engine container."""
    url_path = f'api/v1/solutions/{solution_pk}/scenarios/{scenario_pk}/evaluate/'
    if is_cloud():
        run_eval_engine_cloud(url_path)
    else:
        run_eval_engine_local(url_path, solution_pk)


def run_eval_engine_local(url_path: str, solution_pk: int):
    from app.models import AnalyticsSolution

    tam_file = AnalyticsSolution.objects.get(pk=solution_pk).tam_file

    client = docker.APIClient(base_url='tcp://localhost:2375')

    environment = {
        'EVALJOB_CALLBACK': f'http://host.docker.internal:8000/{url_path}',
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


def run_eval_engine_cloud(url_path: str):
    evaljob_callback = f'https://{settings.AZ_CUSTOM_DOMAIN}/{url_path}'

    data = {
        'location': 'southcentralus',
        'image': settings.EVAL_ENGINE_IMAGE,
        'memory': 8.0,
        'cpu': 2.0,
        'environment_variables': {
            'EVALJOB_CALLBACK': evaljob_callback,
        },
    }

    r = requests.post(
        settings.AZ_FUNC_CREATE_ACI,
        json=data,
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

    grafana_api = GrafanaFace(auth=os.environ.get('GRAFANA_API_KEY'), host=os.environ.get('GRAFANA_HOST'))
    with open(os.environ.get('GRAFANA_TEMPLATE')) as f:
        dashboard = json.load(f)
    dashboard['title'] = title
    return grafana_api.dashboard.update_dashboard({'dashboard': dashboard})


def assign_model_perm(user_or_group, model_or_instance):
    """Assign all permissions of a specific model to a user or group.

    If `model_or_instance` is a model, model-level permissions will be
    assigned. Otherwise, if `model_or_instance` is an instance, object-level
    permissions will be assigned.
    """
    _assign_or_remove_model_perm(True, user_or_group, model_or_instance)


def remove_model_perm(user_or_group, model_or_instance):
    """Remove all permissions of a specific model to a user or group.

    If `model_or_instance` is a model, model-level permissions will be removed.
    Otherwise, if `model_or_instance` is an instance, object-level permissions
    will be removed.
    """
    _assign_or_remove_model_perm(False, user_or_group, model_or_instance)


def _assign_or_remove_model_perm(assign, user_or_group, model_or_instance):
    perm_meth = assign_perm if assign else remove_perm
    all_permissions = get_perms_for_model(model_or_instance)
    for permission in all_permissions:
        if isinstance(model_or_instance, type):
            # Is model class
            perm_meth(permission, user_or_group)
        else:
            # Is model instance
            perm_meth(permission, user_or_group, model_or_instance)


class PowerBI:
    SCOPE = ['https://analysis.windows.net/powerbi/api/.default']

    def __init__(self, solution, user):
        self.solution = solution
        self.user = user

        self._access_token = None
        self._report = None

    @property
    def workspace_id(self):
        return self.solution.workspace_id

    @property
    def report_id(self):
        return self.solution.report_id

    @property
    def roles(self):
        if self.user.is_anonymous:
            return []
        else:
            roles = Role.get_roles_for_user(self.user).filter(name__startswith=self.solution.name)
            return [role.name[len(self.solution.name) + 3:] for role in roles]

    @property
    def username(self):
        return '' if self.user.is_anonymous else self.user.email

    @property
    def client_secret(self):
        return settings.POWERBI_CLIENT_SECRET

    @property
    def client_id(self):
        return settings.POWERBI_CLIENT_ID

    @property
    def tenant_id(self):
        return settings.POWERBI_TENANT_ID

    @property
    def authority(self):
        return f'https://login.microsoftonline.com/{self.tenant_id}'

    @property
    def headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
        }

    @property
    def access_token(self):
        """Returns AAD token using MSAL."""
        if self._access_token is not None:
            return self._access_token

        client = msal.ConfidentialClientApplication(
            self.client_id,
            client_credential=self.client_secret,
            authority=self.authority,
        )

        # Retrieve Access token from cache if available
        response = client.acquire_token_silent(scopes=self.SCOPE, account=None)
        if not response:
            # Make a client call if Access token is not available in cache
            response = client.acquire_token_for_client(scopes=self.SCOPE)
        try:
            self._access_token = response['access_token']
            return self._access_token
        except KeyError:
            raise Exception(response['error_description']) from None

    @property
    def report(self):
        if self._report is not None:
            return self._report

        url = (
            'https://api.powerbi.com/v1.0/myorg/groups/'
            + self.workspace_id
            + '/reports/'
            + self.report_id
        )

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        body = response.json()
        self._report = {
            'embed_url': body['embedUrl'],
            'dataset_id': body['datasetId'],
        }
        return self._report

    def get_embed_token(self):
        """Returns Embed token and Embed URL."""

        if not self.workspace_id or not self.report_id:
            return ''

        report = self.report
        embed_url = report['embed_url']
        dataset_id = report['dataset_id']

        # Get embed token
        body = {'datasets': []}
        if dataset_id:
            body['datasets'].append(
                {
                    'id': dataset_id,
                    'username': self.username,
                    'roles': self.roles,
                    'datasets': [dataset_id],
                }
            )

        body['reports'] = [{'id': self.report_id}]
        body['targetWorkspaces'] = [{'id': self.workspace_id}]

        # Generate Embed token for multiple workspaces, datasets, and reports.
        # Refer https://aka.ms/MultiResourceEmbedToken
        embed_token_url = 'https://api.powerbi.com/v1.0/myorg/GenerateToken'
        response = requests.post(embed_token_url, json=body, headers=self.headers)
        response.raise_for_status()

        body = response.json()
        embed_token = body['token']
        token_expiry = body['expiration']

        return {
            'embedToken': embed_token,
            'embedUrl': embed_url,
            'tokenExpiry': token_expiry,
            'reportId': self.report_id,
        }
